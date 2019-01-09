# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import io
import sys


from cmake_format import commands
from cmake_format import common
from cmake_format import lexer


# --------------------------------------------------
# Middle Layer Parse: digest tokens into block nodes
# --------------------------------------------------


class NodeType(common.EnumObject):
  """
  Enumeration for AST nodes
  """
  _id_map = {}


NodeType.BODY = NodeType(0)
NodeType.WHITESPACE = NodeType(1)
NodeType.COMMENT = NodeType(2)
NodeType.STATEMENT = NodeType(3)
NodeType.FLOW_CONTROL = NodeType(4)
NodeType.FUNNAME = NodeType(10)
NodeType.ARGGROUP = NodeType(5)
NodeType.KWARGGROUP = NodeType(6)
NodeType.ARGUMENT = NodeType(7)
NodeType.KEYWORD = NodeType(8)
NodeType.FLAG = NodeType(9)
NodeType.ONOFFSWITCH = NodeType(11)

# NOTE(josh): These aren't really semantic, but they have structural
# significance that is important in formatting. Since they will have a presence
# in the format tree, we give them a presence in the parse tree as well.
NodeType.LPAREN = NodeType(12)
NodeType.RPAREN = NodeType(13)


class FlowType(common.EnumObject):
  """
  Enumeration for flow control types
  """
  _id_map = {}


FlowType.IF = FlowType(0)
FlowType.WHILE = FlowType(1)
FlowType.FOREACH = FlowType(2)
FlowType.FUNCTION = FlowType(3)
FlowType.MACRO = FlowType(4)


WHITESPACE_TOKENS = (lexer.TokenType.WHITESPACE,
                     lexer.TokenType.NEWLINE)

# TODO(josh): Don't include FORMAT_OFF and FORMAT_ON in comment tokens. They
# wont get reflowed within a comment block so there is no reason to parse them
# as such.
COMMENT_TOKENS = (lexer.TokenType.COMMENT,)
ONOFF_TOKENS = (lexer.TokenType.FORMAT_ON,
                lexer.TokenType.FORMAT_OFF)


CONDITIONAL_KWARGS = commands.make_conditional_spec()


class TreeNode(object):
  """
  A node in the full-syntax-tree.
  """

  def __init__(self, node_type):
    self.node_type = node_type
    self.children = []

  def get_location(self):
    """
    Return the (line, col) of the first token in the subtree rooted at this
    node.
    """
    if self.children:
      return self.children[0].get_location()

    return lexer.SourceLocation((0, 0, 0))

  def count_newlines(self):
    newline_count = 0
    for child in self.children:
      newline_count += child.count_newlines()
    return newline_count

  def __repr__(self):
    return '{}: {}'.format(self.node_type.name, self.get_location())


def consume_whitespace(tokens):
  """
  Consume sequential whitespace, removing tokens from the iniput list and
  returning a whitespace BlockNode
  """

  node = TreeNode(NodeType.WHITESPACE)
  whitespace_tokens = node.children
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    whitespace_tokens.append(tokens.pop(0))

  return node


def consume_comment(tokens):
  """
  Consume sequential comment lines, removing tokens from the input list and
  returning a comment Block
  """

  node = TreeNode(NodeType.COMMENT)
  comment_tokens = node.children
  while tokens and tokens[0].type in COMMENT_TOKENS:
    comment_tokens.append(tokens.pop(0))

    # Multiple comments separated by only one newline are joined together into
    # a single block
    if (len(tokens) > 1
        # pylint: disable=bad-continuation
        and tokens[0].type == lexer.TokenType.NEWLINE
            and tokens[1].type in COMMENT_TOKENS):
      comment_tokens.append(tokens.pop(0))

    # Multiple comments separated only by one newline and some whitespace are
    # joined together into a single block
    # TODO(josh): maybe match only on comment tokens that start at the same
    # column
    elif (len(tokens) > 2
          # pylint: disable=bad-continuation
          and tokens[0].type == lexer.TokenType.NEWLINE
          and tokens[1].type == lexer.TokenType.WHITESPACE
          and tokens[2].type in COMMENT_TOKENS):
      comment_tokens.append(tokens.pop(0))
      comment_tokens.append(tokens.pop(0))
  return node


def consume_onoff(tokens):
  """
  Consume a 'cmake-format: [on|off]' comment
  """

  node = TreeNode(NodeType.ONOFFSWITCH)
  node.children.append(tokens.pop(0))
  return node


def next_is_trailing_comment(tokens):
  """
  Return true if there is a trailing comment in the token stream
  """

  if not tokens:
    return False

  if tokens[0].type in [lexer.TokenType.COMMENT,
                        lexer.TokenType.BRACKET_COMMENT]:
    return True

  if len(tokens) < 2:
    return False

  if (tokens[0].type == lexer.TokenType.WHITESPACE
      and tokens[1].type in [lexer.TokenType.COMMENT,
                             lexer.TokenType.BRACKET_COMMENT]):
    return True

  return False


def consume_trailing_comment(parent, tokens):
  """
  Consume sequential comment lines, removing tokens from the input list and
  appending the resulting node as a child to the provided parent
  """
  if not next_is_trailing_comment(tokens):
    return

  if tokens[0].type == lexer.TokenType.WHITESPACE:
    parent.children.append(tokens.pop(0))

  node = TreeNode(NodeType.COMMENT)
  parent.children.append(node)

  match_tokens = (lexer.TokenType.COMMENT,
                  lexer.TokenType.BRACKET_COMMENT)
  comment_tokens = node.children

  while tokens and tokens[0].type in match_tokens:
    comment_tokens.append(tokens.pop(0))

    # Multiple comments separated by only one newline are joined together into
    # a single block
    if (len(tokens) > 1
        # pylint: disable=bad-continuation
        and tokens[0].type == lexer.TokenType.NEWLINE
            and tokens[1].type in match_tokens):
      comment_tokens.append(tokens.pop(0))

    # Multiple comments separated only by one newline and some whitespace are
    # joined together into a single block
    # TODO(josh): maybe match only on comment tokens that start at the same
    # column?
    elif (len(tokens) > 2
          # pylint: disable=bad-continuation
          and tokens[0].type == lexer.TokenType.NEWLINE
          and tokens[1].type == lexer.TokenType.WHITESPACE
          and tokens[2].type in match_tokens):
      comment_tokens.append(tokens.pop(0))
      comment_tokens.append(tokens.pop(0))


def get_normalized_kwarg(token):
  """
  Return uppercase token spelling if it is a word, otherwise return None
  """

  if (token.type == lexer.TokenType.UNQUOTED_LITERAL
      and token.spelling.startswith('-')):
    return token.spelling.lower()

  if token.type != lexer.TokenType.WORD:
    return None

  return token.spelling.upper()


def kwarg_breaks_stack(kwarg, currspec, argstack=None):
  if argstack is None:
    return False

  if kwarg is None:
    return False

  if isinstance(currspec, dict) and kwarg in currspec:
    return False

  for cmdspec in argstack[::-1]:
    if (isinstance(cmdspec, commands.CommandSpec)
        and cmdspec.name == 'COMMAND'
        and kwarg.startswith('--')):
      return True

    if isinstance(cmdspec, dict) and kwarg in cmdspec:
      if kwarg == "STREQUAL":
        print(currspec)
      return True

  return False


def token_is_flag(normalized_token, cmdspec):
  if normalized_token is None:
    return False

  if not isinstance(cmdspec, commands.CommandSpec):
    return False

  if (cmdspec.name == 'COMMAND'
      and len(normalized_token) > 1
      and normalized_token[0] == '-'
      and normalized_token[1] != '-'):
    return True

  return cmdspec.is_flag(normalized_token)


def token_is_kwarg(normalized_token, cmdspec):
  if normalized_token is None:
    return False

  if not isinstance(cmdspec, commands.CommandSpec):
    return False

  if (cmdspec.name == 'COMMAND'
      and normalized_token.startswith('--')):
    return True

  return cmdspec.is_kwarg(normalized_token)


def is_full(pargs, spec):
  """
  Return true if the current node is full due to command specification
  """

  if isinstance(spec, int):
    if pargs >= spec:
      return True
  elif hasattr(spec, 'pargs'):
    spec_pargs = getattr(spec, 'pargs')
    if isinstance(spec_pargs, int) and pargs >= spec_pargs:
      return True

  return False


def consume_arguments(node, tokens, cmdspec, argstack=None):
  """
  Consume a parenthetical group of arguments.
  """

  if argstack is None:
    argstack = []

  children = node.children

  # Number of positional arguments accumulated for the current command
  pargs = 0

  while tokens:
    if tokens[0].type == lexer.TokenType.LEFT_PAREN:
      # LEFT_PAREN signals the start of a conditional group

      # NOTE(josh): since parenthetical groups act as positional arguments,
      # if the current compliment of positional arguments is full, we can
      # go ahead and close this node...
      if is_full(pargs, cmdspec):
        return

      subtree = TreeNode(NodeType.ARGGROUP)
      lparen = TreeNode(NodeType.LPAREN)
      lparen.children.append(tokens.pop(0))
      subtree.children.append(lparen)

      # NOTE(josh): we pass in conditional cmdspec since argument groups
      # aren't arbitrary and are only allowed for conditional statements.
      # I have a feeling this might change in the future as the cmake language
      # develops further.
      consume_arguments(subtree, tokens, CONDITIONAL_KWARGS)
      children.append(subtree)

      if tokens[0].type != lexer.TokenType.RIGHT_PAREN:
        raise ValueError(
            "Unexpected {} token at {}, expecting r-paren, got {}"
            .format(tokens[0].type.name, tokens[0].get_location(),
                    tokens[0].content))
      rparen = TreeNode(NodeType.RPAREN)
      rparen.children.append(tokens.pop(0))
      subtree.children.append(rparen)

      # NOTE(josh): parenthetical groups can have trailing comments because
      # they have closing punctuation
      consume_trailing_comment(subtree, tokens)
      pargs += 1
      continue

    if tokens[0].type == lexer.TokenType.RIGHT_PAREN:
      # RIGHT_PARENT signals the end of the currently opened parenthentical
      # group. This case is handled by the caller.
      return

    if tokens[0].type in WHITESPACE_TOKENS:
      children.append(tokens.pop(0))
      continue

    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):

      # NOTE(josh): if the current command is full, then break out of it and
      # associate the comment with the parent command
      if is_full(pargs, cmdspec):
        return

      child = TreeNode(NodeType.COMMENT)
      children.append(child)
      child.children.append(tokens.pop(0))
      continue

    kwarg = get_normalized_kwarg(tokens[0])
    if token_is_kwarg(kwarg, cmdspec):
      subtree = TreeNode(NodeType.KWARGGROUP)
      children.append(subtree)

      child = TreeNode(NodeType.KEYWORD)
      subtree.children.append(child)
      child.children.append(tokens.pop(0))
      # NOTE(josh): don't allow keywords to have trailing comments. This
      # complicates our ability to compute the location of the cursor where
      # to write the next element. In particular the reflow() cursor returned
      # will point to the end of the comment, but we really want to know
      # where the keyword ends, so that we can follow that column for each
      # child. Instead we treat the keyword comment as a positional comment
      # which makes it a node at the same level as the rest of it's children.
      # consume_trailing_comment(child, tokens)

      consume_arguments(subtree, tokens, cmdspec.get(kwarg),
                        argstack + [cmdspec])
      # NOTE(josh): kwarg groups can't have trailing comments because they
      # have no closing puncutation
      continue

    if token_is_flag(kwarg, cmdspec):
      child = TreeNode(NodeType.FLAG)
      children.append(child)
      child.children.append(tokens.pop(0))
      consume_trailing_comment(child, tokens)
      continue

    if kwarg_breaks_stack(kwarg, cmdspec, argstack):
      # NOTE(josh): the next token matches a keyword of some command
      # higher up in the stack, so we are done here. We will return from
      # every callee up to the caller with the approprate cmdspec.
      return

    # The current token is an argument and if it is a WORD then it doesn't
    # match a keyword of any specification in the stack so it must be
    # a positional argument

    # If the current node has a full compliment of positional arguments, then
    # the next argument must belong to a node higher up in the call stack.
    if is_full(pargs, cmdspec):
      return

    child = TreeNode(NodeType.ARGUMENT)
    children.append(child)
    child.children.append(tokens.pop(0))
    consume_trailing_comment(child, tokens)
    pargs += 1

  raise ValueError(
      "Token stream expired while parsing statement arguments starting at {}"
      .format(node.get_location()))


def consume_statement(tokens, cmdspec):
  """
  Consume a complete statement, removing tokens from the input list and
  returning a statement Block
  """
  node = TreeNode(NodeType.STATEMENT)

  # Consume the function name
  fnname = tokens[0].spelling.lower()

  funnode = TreeNode(NodeType.FUNNAME)
  funnode.children.append(tokens.pop(0))
  node.children.append(funnode)

  # Consume whitespace up to the parenthesis
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    node.children.append(tokens.pop(0))

  # TODO(josh): should the parens belong to the statement node or the
  # group node?
  if tokens[0].type != lexer.TokenType.LEFT_PAREN:
    raise ValueError(
        "Unexpected {} token at {}, expecting l-paren, got {}"
        .format(tokens[0].type.name, tokens[0].get_location(),
                repr(tokens[0].content)))

  lparen = TreeNode(NodeType.LPAREN)
  lparen.children.append(tokens.pop(0))
  node.children.append(lparen)

  subtree = TreeNode(NodeType.ARGGROUP)
  node.children.append(subtree)
  consume_arguments(subtree, tokens, cmdspec.get(fnname, None), [])

  # NOTE(josh): technically we may have a statement specification with
  # an exact number of arguments. At this point we have broken out of that
  # statement but we might have some comments or whitespace to consume

  while tokens and tokens[0].type != lexer.TokenType.RIGHT_PAREN:
    if tokens[0].type in WHITESPACE_TOKENS:
      node.children.append(tokens.pop(0))
      continue

    if tokens[0].type in COMMENT_TOKENS:
      cnode = consume_comment(tokens)
      node.children.append(cnode)
      continue

    raise ValueError(
        "Unexpected {} token at {}, expecting r-paren, got {}"
        .format(tokens[0].type.name, tokens[0].get_location(),
                repr(tokens[0].content)))

  assert tokens, "Unexpected end of token stream while parsing statement"
  assert tokens[0].type == lexer.TokenType.RIGHT_PAREN, \
      ("Unexpected {} token at {}, expecting r-paren, got {}"
       .format(tokens[0].type.name, tokens[0].get_location(),
               repr(tokens[0].content)))

  rparen = TreeNode(NodeType.RPAREN)
  rparen.children.append(tokens.pop(0))
  node.children.append(rparen)
  consume_trailing_comment(node, tokens)

  return node


def consume_ifblock(tokens, cmdspec):
  """
  Consume tokens and return a flow control tree. ``IF`` statements are special
  because they have interior ``ELSIF`` and ``ELSE`` blocks, while all other
  flow control have a single body.
  """

  node = TreeNode(NodeType.FLOW_CONTROL)
  children = node.children
  breakset = ("ELSE", "ELSEIF", "ENDIF")

  while tokens and tokens[0].spelling.upper() != "ENDIF":
    stmt = consume_statement(tokens, cmdspec)
    children.append(stmt)
    body = consume_body(tokens, cmdspec, breakset)
    children.append(body)
  stmt = consume_statement(tokens, cmdspec)
  children.append(stmt)

  return node


def consume_flowcontrol(tokens, cmdspec):
  """
  Consume tokens and return a flow control tree. A flow control tree starts
  and ends with a statement node, and contains one or more body nodes. An if
  statement is the only flow control that includes multiple body nodes and they
  are separated by either else or elseif nodes.
  """
  flowtype = FlowType.from_name(tokens[0].spelling.upper())
  if flowtype is FlowType.IF:
    return consume_ifblock(tokens, cmdspec)

  node = TreeNode(NodeType.FLOW_CONTROL)
  children = node.children
  endflow = 'END' + flowtype.name
  stmt = consume_statement(tokens, cmdspec)
  children.append(stmt)
  body = consume_body(tokens, cmdspec, (endflow,))
  children.append(body)
  stmt = consume_statement(tokens, cmdspec)
  children.append(stmt)

  return node


def consume_body(tokens, cmdspec, breakset=None):
  """
  Consume tokens and return a tree of nodes. Top-level consumer parsers
  comments, whitespace, statements, and flow control blocks.
  """
  if breakset is None:
    breakset = ()

  tree = TreeNode(NodeType.BODY)
  blocks = tree.children

  while tokens:
    token = tokens[0]
    if token.type in WHITESPACE_TOKENS:
      node = consume_whitespace(tokens)
      blocks.append(node)
    elif token.type in COMMENT_TOKENS:
      node = consume_comment(tokens)
      blocks.append(node)
    elif token.type in ONOFF_TOKENS:
      node = consume_onoff(tokens)
      blocks.append(node)
    elif token.type == lexer.TokenType.BRACKET_COMMENT:
      node = TreeNode(NodeType.COMMENT)
      node.children = [tokens.pop(0)]
      blocks.append(node)
    elif token.type == lexer.TokenType.WORD:
      upper = token.spelling.upper()
      if upper in breakset:
        return tree
      elif FlowType.get(upper) is not None:
        subtree = consume_flowcontrol(tokens, cmdspec)
        blocks.append(subtree)
      else:
        subtree = consume_statement(tokens, cmdspec)
        blocks.append(subtree)
    elif token.type == lexer.TokenType.BYTEORDER_MARK:
      tokens.pop(0)
    else:
      assert False, ("Unexpected {} token at {}:{}"
                     .format(tokens[0].type.name,
                             tokens[0].begin.line, tokens[0].begin.col))

  return tree

# ------------------
# Frontend utilities
# ------------------


def parse(tokens, cmdspec=None):
  """
  digest tokens, then layout the digested blocks.
  """
  if cmdspec is None:
    cmdspec = commands.get_fn_spec()

  return consume_body(tokens, cmdspec)


def dump_tree(nodes, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for idx, node in enumerate(nodes):
    outfile.write(indent)
    if idx + 1 == len(nodes):
      outfile.write('└─ ')
    else:
      outfile.write('├─ ')
    noderep = repr(node)
    if sys.version_info[0] < 3:
      # python2
      outfile.write(getattr(noderep, 'decode')('utf-8'))
    else:
      # python3
      outfile.write(noderep)
    outfile.write('\n')

    if not hasattr(node, 'children'):
      continue

    if idx + 1 == len(nodes):
      dump_tree(node.children, outfile, indent + '    ')
    else:
      dump_tree(node.children, outfile, indent + '│   ')


def tree_string(nodes):
  outfile = io.StringIO()
  dump_tree(nodes, outfile)
  return outfile.getvalue()


def has_nontoken_children(node):
  if not hasattr(node, 'children'):
    return False

  for child in node.children:
    if isinstance(child, TreeNode):
      return True

  return False


def dump_tree_for_test(nodes, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for node in nodes:
    if not isinstance(node, TreeNode):
      continue
    outfile.write(indent)
    outfile.write('({}, ['.format(node.node_type))
    if has_nontoken_children(node):
      outfile.write('\n')
      dump_tree_for_test(node.children, outfile, indent + '    ')
      outfile.write(indent)
    outfile.write(']),\n')


def test_string(nodes):
  outfile = io.StringIO()
  dump_tree_for_test(nodes, outfile, indent=(' ' * 10))
  return outfile.getvalue()


def main():
  """
  Dump digested tokens or full-syntax-tree to stdout for debugging purposes.
  """
  import argparse
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('infile')
  args = parser.parse_args()

  with open(args.infile, 'r') as infile:
    tokens = lexer.tokenize(infile.read())
    rootnode = parse(tokens)

  dump_tree([rootnode], sys.stdout)


if __name__ == '__main__':
  main()
