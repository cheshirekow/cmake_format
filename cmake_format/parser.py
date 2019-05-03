# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging
import re
import sys

from cmake_format import common
from cmake_format import lexer


logger = logging.getLogger("cmake_format")

if sys.version_info[0] < 3:
  STRING_TYPES = (str, unicode)
else:
  STRING_TYPES = (str,)

IMPLICIT_PARG_TYPES = STRING_TYPES + (int,)


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
NodeType.PARGGROUP = NodeType(14)
NodeType.FLAGGROUP = NodeType(15)
NodeType.PARENGROUP = NodeType(16)
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


class TreeNode(object):
  """
  A node in the full-syntax-tree.
  """

  def __init__(self, node_type, sortable=False):
    self.node_type = node_type
    self.children = []
    self.sortable = sortable

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
    if self.sortable:
      return ('{}: {}, sortable'
              .format(self.node_type.name, self.get_location()))

    return '{}: {}'.format(self.node_type.name, self.get_location())


def consume_whitespace(tokens):
  """
  Consume sequential whitespace, removing tokens from the input list and
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


def is_valid_trailing_comment(token):
  """
  Return true if the token is a valid trailing comment
  """
  return (token.type in (lexer.TokenType.COMMENT,
                         lexer.TokenType.BRACKET_COMMENT) and
          not comment_is_tag(token))


def next_is_trailing_comment(tokens):
  """
  Return true if there is a trailing comment in the token stream
  """

  if not tokens:
    return False

  if is_valid_trailing_comment(tokens[0]):
    return True

  if len(tokens) < 2:
    return False

  if (tokens[0].type == lexer.TokenType.WHITESPACE
      and is_valid_trailing_comment(tokens[1])):
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
  comment_tokens = node.children

  while tokens and is_valid_trailing_comment(tokens[0]):
    comment_tokens.append(tokens.pop(0))

    # Multiple comments separated by only one newline are joined together into
    # a single block
    if (len(tokens) > 1 and
        tokens[0].type == lexer.TokenType.NEWLINE and
        is_valid_trailing_comment(tokens[1])):
      comment_tokens.append(tokens.pop(0))

    # Multiple comments separated only by one newline and some whitespace are
    # joined together into a single block
    # TODO(josh): maybe match only on comment tokens that start at the same
    # column?
    elif (len(tokens) > 2 and
          tokens[0].type == lexer.TokenType.NEWLINE and
          tokens[1].type == lexer.TokenType.WHITESPACE and
          is_valid_trailing_comment(tokens[2])):
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


def should_break(token, breakstack):
  """
  Return true if any function in breakstack evaluates to true on the current
  token. Otherwise return false.
  """
  for breakcheck in breakstack[::-1]:
    if breakcheck(token):
      return True
  return False


def pargs_are_full(npargs, nconsumed):
  if isinstance(npargs, int):
    return nconsumed >= npargs

  assert isinstance(npargs, STRING_TYPES), (
      "Unexpected npargs type {}".format(type(npargs)))

  if npargs == "?":
    return nconsumed >= 1

  assert npargs in ("*", "+"), ("Unexepected npargs {}".format(npargs))
  return False


def npargs_is_exact(npargs):
  """
  Return true if npargs has an exact specification
  """
  return isinstance(npargs, int)


LINE_TAG = re.compile(r"#\s*(cmake-format|cmf): ([^\n]*)")
BRACKET_TAG = re.compile(r"#\[(=*)\[(cmake-format|cmf):(.*)\]\1\]")


def get_tag(token):
  """
  If the token is a comment with one of the cmake-format tag forms, then
  extract the tag.
  """
  if token.type is lexer.TokenType.COMMENT:
    match = LINE_TAG.match(token.spelling)
    if match:
      return match.group(2).strip().lower()
  elif token.type is lexer.TokenType.BRACKET_COMMENT:
    match = BRACKET_TAG.match(token.spelling)
    if match:
      return match.group(3).strip().lower()

  return None


def comment_is_tag(token):
  """
  Return true if the comment token has one of the tag-forms:

  # cmake-format: <tag>
  # cmf: <tag>
  #[[cmake-format:<tag>]]
  #[[cmf:<tag>]]
  """
  return get_tag(token) is not None


def only_comments_and_whitespace_remain(tokens, breakstack):
  skip_tokens = (lexer.TokenType.WHITESPACE,
                 lexer.TokenType.NEWLINE,
                 lexer.TokenType.COMMENT,
                 lexer.TokenType.BRACKET_COMMENT)

  for token in tokens:
    if token.type in skip_tokens:
      continue
    elif should_break(token, breakstack):
      return True
    else:
      return False
  return True


def consume_whitespace_and_comments(tokens, tree):
  """
  Consume any whitespace or comments that occur at the current depth
  """
  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens:
    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(tokens.pop(0))
      continue
    break


def iter_semantic_tokens(tokens):
  """
  Return a generator over the list of tokens yielding only those that
  have semantic meaning
  """
  skip_tokens = (lexer.TokenType.WHITESPACE,
                 lexer.TokenType.NEWLINE,
                 lexer.TokenType.COMMENT,
                 lexer.TokenType.BRACKET_COMMENT)

  for token in tokens:
    if token.type in skip_tokens:
      continue
    yield token


def get_first_semantic_token(tokens):
  """
  Return the first token with semantic meaning
  """

  for token in iter_semantic_tokens(tokens):
    return token
  return None


def parse_pattern(tokens, breakstack):
  """
  ::

    [PATTERN <pattern> | REGEX <regex>]
    [EXCLUDE] [PERMISSIONS <permissions>...]
  """
  return parse_standard(
      tokens,
      npargs='+',
      kwargs={"PERMISSIONS": PositionalParser('+'), },
      flags=["EXCLUDE"],
      breakstack=breakstack
  )


def parse_positionals(tokens, npargs, flags, breakstack, sortable=False):
  """
  Parse a continuous sequence of `npargs` positional arguments. If npargs is
  an integer we will consume exactly that many arguments. If it is not an
  integer then it is a string meaning:

  * "?": zero or one
  * "*": zero or more
  * "+": one or more
  """

  tree = TreeNode(NodeType.PARGGROUP, sortable=sortable)
  nconsumed = 0

  # Strip off any preceeding whitespace (note that in most cases this has
  # already been done but in some cases (such ask kwarg subparser) where
  # it hasn't
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))

  # If the first non-whitespace token is a cmake-format tag annotating
  # sortability, then parse it out here and record the annotation
  if tokens and get_tag(tokens[0]) in ("sortable", "sort"):
    tree.sortable = True
  elif tokens and get_tag(tokens[0]) in ("unsortable", "unsort"):
    tree.sortable = False

  while tokens:
    # Break if we have consumed   enough positional arguments
    if pargs_are_full(npargs, nconsumed):
      break

    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      # NOTE(josh): if npargs is an exact number of arguments, then we
      # shouldn't break on kwarg match from a parent parser. Instead, we should
      # consume the token. This is a hack to deal with
      # ```install(RUNTIME COMPONENT runtime)``. In this case the second
      # occurance of "runtime" should not match the ``RUNTIME`` keyword
      # and should not break the positional parser.
      # TODO(josh): this is kind of hacky because it will force the positional
      # parser to consume a right parenthesis and will lead to parse errors
      # in the event of a missing positional argument. Such errors will be
      # difficult to debug for the user.
      if not npargs_is_exact(npargs):
        break
      elif tokens[0].type == lexer.TokenType.RIGHT_PAREN:
        break

    # If this is the start of a parenthetical group, then parse the group
    # NOTE(josh): syntatically this probably shouldn't be allowed here, but
    # cmake seems to accept it so we probably should too.
    if tokens[0].type == lexer.TokenType.LEFT_PAREN:
      subtree = parse_parengroup(tokens, breakstack)
      tree.children.append(subtree)
      continue

    # Otherwise we will consume the token
    token = tokens.pop(0)

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if token.type in WHITESPACE_TOKENS:
      tree.children.append(token)
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if token.type in (lexer.TokenType.COMMENT,
                      lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(token)
      continue

    # Otherwise is it is a positional argument, so add it to the tree as such
    if get_normalized_kwarg(token) in flags:
      child = TreeNode(NodeType.FLAG)
    else:
      child = TreeNode(NodeType.ARGUMENT)

    child.children.append(token)
    consume_trailing_comment(child, tokens)
    tree.children.append(child)
    nconsumed += 1
  return tree


def parse_positional_tuples(tokens, npargs, ntup, flags, breakstack):
  """
  Parse a continuous sequence of `npargs` positional argument pairs.
  If npargs is an integer we will consume exactly that many arguments.
  If it is not an integer then it is a string meaning:

  * "?": zero or one
  * "*": zero or more
  * "+": one or more
  """

  tree = TreeNode(NodeType.PARGGROUP)
  subtree = None
  active_depth = tree

  npargs_consumed = 0
  ntup_consumed = 0

  while tokens:
    # Break if we have consumed enough positional arguments
    if pargs_are_full(npargs, npargs_consumed):
      break

    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # Otherwise we will consume the token
    token = tokens.pop(0)

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if token.type in WHITESPACE_TOKENS:
      active_depth.children.append(token)
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if token.type in (lexer.TokenType.COMMENT,
                      lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(token)
      continue

    if subtree is None:
      subtree = TreeNode(NodeType.PARGGROUP)
      tree.children.append(subtree)
      ntup_consumed = 0

    # Otherwise is it is a positional argument, so add it to the tree as such
    if get_normalized_kwarg(token) in flags:
      child = TreeNode(NodeType.FLAG)
    else:
      child = TreeNode(NodeType.ARGUMENT)

    child.children.append(token)
    consume_trailing_comment(child, tokens)
    subtree.children.append(child)
    ntup_consumed += 1

    if ntup_consumed > ntup:
      npargs_consumed += 1
      subtree = None

  return tree


def parse_kwarg(tokens, word, subparser, breakstack):
  """
  Parse a standard `KWARG arg1 arg2 arg3...` style keyword argument list.
  """
  assert tokens[0].spelling.upper() == word.upper()

  tree = TreeNode(NodeType.KWARGGROUP)
  kwnode = TreeNode(NodeType.KEYWORD)
  kwnode.children.append(tokens.pop(0))
  tree.children.append(kwnode)
  # consume_trailing_comment(kwnode, tokens)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))

  ntokens = len(tokens)
  subtree = subparser(tokens, breakstack)
  if len(tokens) < ntokens:
    tree.children.append(subtree)
  return tree


def parse_flags(tokens, flags, breakstack):
  """
  Parse a continuous sequence of flags
  """

  tree = TreeNode(NodeType.FLAGGROUP)
  while tokens:
    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # Break if the next token is not a known flag
    if tokens[0].spelling.upper() not in flags:
      break

    # Otherwise is it is a flag, so add it to the tree as such
    child = TreeNode(NodeType.FLAG)
    child.children.append(tokens.pop(0))
    consume_trailing_comment(child, tokens)
    tree.children.append(child)

  return tree


def parse_standard(tokens, npargs, kwargs, flags, breakstack):
  """
  Standard parser for the commands in the form of::

      command_name(parg1 parg2 parg3...
                   KEYWORD1 kwarg1 kwarg2...
                   KEYWORD2 kwarg3 kwarg4...
                   FLAG1 FLAG2 FLAG3)

  The parser starts off as a positional parser. If a keyword or flag is
  encountered the positional parser is popped off the parse stack. If it was
  a keyword then the keyword parser is pushed on the parse stack. If it was
  a flag than a new flag parser is pushed onto the stack.
  """

  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  flags = [flag.upper() for flag in flags]
  kwarg_breakstack = breakstack + [KwargBreaker(list(kwargs.keys()) + flags)]
  positional_breakstack = breakstack + [KwargBreaker(list(kwargs.keys()))]

  while tokens:
    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # If it's a comment, then add it at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    ntokens = len(tokens)
    # NOTE(josh): each flag is also stored in kwargs as with a positional parser
    # of size zero. This is a legacy thing that should be removed, but for now
    # just make sure we check flags first.
    word = get_normalized_kwarg(tokens[0])
    if word in kwargs:
      subtree = parse_kwarg(tokens, word, kwargs[word], kwarg_breakstack)
    else:
      subtree = parse_positionals(tokens, npargs, flags, positional_breakstack)

    assert len(tokens) < ntokens
    tree.children.append(subtree)
  return tree


def parse_parengroup(tokens, breakstack):  # pylint: disable=unused-argument
  """
  Consume a parenthetical group of arguments from `tokens` and return the
  parse subtree rooted at this group.  `argstack` contains a stack of all
  early break conditions that are currently "opened".
  """

  assert tokens[0].type == lexer.TokenType.LEFT_PAREN
  tree = TreeNode(NodeType.PARENGROUP)
  lparen = TreeNode(NodeType.LPAREN)
  lparen.children.append(tokens.pop(0))
  tree.children.append(lparen)

  subtree = parse_conditional(tokens, [ParenBreaker()])
  tree.children.append(subtree)

  if tokens[0].type != lexer.TokenType.RIGHT_PAREN:
    raise ValueError(
        "Unexpected {} token at {}, expecting r-paren, got {}"
        .format(tokens[0].type.name, tokens[0].get_location(),
                tokens[0].content))
  rparen = TreeNode(NodeType.RPAREN)
  rparen.children.append(tokens.pop(0))
  tree.children.append(rparen)

  # NOTE(josh): parenthetical groups can have trailing comments because
  # they have closing punctuation
  consume_trailing_comment(tree, tokens)

  return tree


CONDITIONAL_FLAGS = [
    "COMMAND",
    "DEFINED",
    "EQUAL",
    "EXISTS",
    "GREATER",
    "LESS",
    "IS_ABSOLUTE",
    "IS_DIRECTORY",
    "IS_NEWER_THAN",
    "IS_SYMLINK",
    "MATCHES",
    "NOT",
    "POLICY",
    "STRLESS",
    "STRGREATER",
    "STREQUAL",
    "TARGET",
    "TEST",
    "VERSION_EQUAL",
    "VERSION_GREATER",
    "VERSION_LESS",
]


def parse_conditional(tokens, breakstack):
  """
  Parser for the commands that take conditional arguments. Similar to the
  standard parser but it understands parentheses and can generate
  parenthentical groups::

      while(CONDITION1 AND (CONDITION2 OR CONDITION3)
            OR (CONDITION3 AND (CONDITION4 AND CONDITION5)
            OR CONDITION6)
  """
  kwargs = {
      'AND': parse_conditional,
      'OR': parse_conditional
  }
  flags = list(CONDITIONAL_FLAGS)
  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  flags = [flag.upper() for flag in flags]
  breaker = KwargBreaker(list(kwargs.keys()))
  child_breakstack = breakstack + [breaker]

  while tokens:
    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # If it's a comment, then add it at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    # If this is the start of a parenthetical group, then parse the group
    if tokens[0].type == lexer.TokenType.LEFT_PAREN:
      subtree = parse_parengroup(tokens, breakstack)
      tree.children.append(subtree)
      continue

    ntokens = len(tokens)
    word = get_normalized_kwarg(tokens[0])
    if word in kwargs:
      subtree = parse_kwarg(tokens, word, kwargs[word], child_breakstack)
      assert len(tokens) < ntokens
      tree.children.append(subtree)
      continue

    # Otherwise is it is a positional argument, so add it to the tree as such
    token = tokens.pop(0)
    if get_normalized_kwarg(token) in flags:
      child = TreeNode(NodeType.FLAG)
    else:
      child = TreeNode(NodeType.ARGUMENT)

    child.children.append(token)
    consume_trailing_comment(child, tokens)
    tree.children.append(child)

  return tree


def parse_shell_flags(tokens, breakstack):
  """
  Parse a continuous sequence of flags
  """
  tree = TreeNode(NodeType.FLAGGROUP)
  while tokens:
    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # Break if the next token is not a flag
    if not tokens[0].spelling.startswith("-"):
      break

    # Break if the next token is a long flag
    if tokens[0].spelling.startswith("--"):
      break

    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # Otherwise is it is a flag, so add it to the tree as such
    child = TreeNode(NodeType.FLAG)
    child.children.append(tokens.pop(0))
    consume_trailing_comment(child, tokens)
    tree.children.append(child)

  return tree


def is_shell_flag(token):
  return token.spelling.startswith("-")


def parse_shell_kwarg(tokens, breakstack):
  """
  Parse a standard `--long-flag foo bar baz` sequence
  """
  assert tokens[0].spelling.startswith("--")

  tree = TreeNode(NodeType.KWARGGROUP)
  kwnode = TreeNode(NodeType.KEYWORD)
  kwnode.children.append(tokens.pop(0))
  tree.children.append(kwnode)

  ntokens = len(tokens)
  subtree = parse_positionals(tokens, "*", [], breakstack + [is_shell_flag])
  if len(tokens) < ntokens:
    tree.children.append(subtree)
  return tree


def parse_shell_command(tokens, breakstack):
  """
  Parser for the COMMAND kwarg lists in the form of::

      COMMAND foo --long-flag1 arg1 arg2 --long-flag2 -a -b -c arg3 arg4

  The parser acts very similar to a standard parser where `--xxx` is treated
  as a keyword argument and `-x` is treated as a flag.
  """
  return parse_positionals(tokens, '*', [], breakstack)


def deprecated_parse_shell_command(tokens, breakstack):
  """
  Parser for the COMMAND kwarg lists in the form of::

      COMMAND foo --long-flag1 arg1 arg2 --long-flag2 -a -b -c arg3 arg4

  The parser acts very similar to a standard parser where `--xxx` is treated
  as a keyword argument and `-x` is treated as a flag.
  """

  # TODO(josh): remove dead code, or figure out when to enable it
  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  while tokens:
    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    ntokens = len(tokens)
    if tokens[0].spelling == "--":
      subtree = parse_positionals(tokens, "*", [], breakstack)
    elif tokens[0].spelling.startswith("--"):
      subtree = parse_shell_kwarg(tokens, breakstack)
    elif tokens[0].spelling.startswith("-"):
      subtree = parse_shell_flags(tokens, breakstack)
    else:
      subtree = parse_positionals(tokens, "*", [], breakstack + [is_shell_flag])

    assert len(tokens) < ntokens, "at {}".format(tokens[0])
    tree.children.append(subtree)
  return tree


class PositionalParser(object):
  def __init__(self, npargs=None, flags=None, sortable=False):
    if npargs is None:
      npargs = "*"
    if flags is None:
      flags = []

    self.npargs = npargs
    self.flags = flags
    self.sortable = sortable

  def __call__(self, tokens, breakstack):
    return parse_positionals(tokens, self.npargs, self.flags, breakstack,
                             self.sortable)


class PositionalTupleParser(object):
  def __init__(self, ntup, npargs=None, flags=None):
    if npargs is None:
      npargs = "*"
    if flags is None:
      flags = []

    self.npargs = npargs
    self.ntup = ntup
    self.flags = flags

  def __call__(self, tokens, breakstack):
    return parse_positional_tuples(tokens, self.npargs, self.ntup, self.flags,
                                   breakstack)


class StandardParser(object):
  def __init__(self, npargs=None, kwargs=None, flags=None, doc=None):
    if npargs is None:
      npargs = "*"
    if flags is None:
      flags = []
    if kwargs is None:
      kwargs = {}

    self.npargs = npargs
    self.kwargs = kwargs
    self.flags = flags
    self.doc = doc

  def __call__(self, tokens, breakstack):
    return parse_standard(tokens, self.npargs, self.kwargs, self.flags,
                          breakstack)


class ParenBreaker(object):
  """
  Callable that returns true if the supplied token is a right parenthential
  """

  def __call__(self, token):
    return token.type == lexer.TokenType.RIGHT_PAREN


class KwargBreaker(object):
  """
  Callable that returns true if the supplied token is in the list of keywords,
  ignoring case.
  """

  def __init__(self, kwargs):
    self.kwargs = [kwarg.upper() for kwarg in kwargs]

  def __call__(self, token):
    return token.spelling.upper() in self.kwargs


def consume_statement(tokens, parse_db):
  """
  Consume a complete statement, removing tokens from the input list and
  returning a STATEMENT node.
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

  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    node.children.append(tokens.pop(0))
    continue

  breakstack = [ParenBreaker()]
  parse_fun = parse_db.get(fnname, PositionalParser())
  subtree = parse_fun(tokens, breakstack)
  node.children.append(subtree)

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

  assert tokens, (
      "Unexpected end of token stream while parsing statement:\n {}"
      .format(tree_string([node])))
  assert tokens[0].type == lexer.TokenType.RIGHT_PAREN, \
      ("Unexpected {} token at {}, expecting r-paren, got {}"
       .format(tokens[0].type.name, tokens[0].get_location(),
               repr(tokens[0].content)))

  rparen = TreeNode(NodeType.RPAREN)
  rparen.children.append(tokens.pop(0))
  node.children.append(rparen)
  consume_trailing_comment(node, tokens)

  return node


def consume_ifblock(tokens, parse_db):
  """
  Consume tokens and return a flow control tree. ``IF`` statements are special
  because they have interior ``ELSIF`` and ``ELSE`` blocks, while all other
  flow control have a single body.
  """

  tree = TreeNode(NodeType.FLOW_CONTROL)
  breakset = ("ELSE", "ELSEIF", "ENDIF")

  while tokens and tokens[0].spelling.upper() != "ENDIF":
    stmt = consume_statement(tokens, parse_db)
    tree.children.append(stmt)
    body = consume_body(tokens, parse_db, breakset)
    tree.children.append(body)

  if tokens:
    stmt = consume_statement(tokens, parse_db)
    tree.children.append(stmt)

  return tree


def consume_flowcontrol(tokens, parse_db):
  """
  Consume tokens and return a flow control tree. A flow control tree starts
  and ends with a statement node, and contains one or more body nodes. An if
  statement is the only flow control that includes multiple body nodes and they
  are separated by either else or elseif nodes.
  """
  flowtype = FlowType.from_name(tokens[0].spelling.upper())
  if flowtype is FlowType.IF:
    return consume_ifblock(tokens, parse_db)

  node = TreeNode(NodeType.FLOW_CONTROL)
  children = node.children
  endflow = 'END' + flowtype.name
  stmt = consume_statement(tokens, parse_db)
  children.append(stmt)
  body = consume_body(tokens, parse_db, (endflow,))
  children.append(body)
  stmt = consume_statement(tokens, parse_db)
  children.append(stmt)

  return node


def consume_body(tokens, parse_db, breakset=None):
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
      if FlowType.get(upper) is not None:
        subtree = consume_flowcontrol(tokens, parse_db)
        blocks.append(subtree)
      else:
        subtree = consume_statement(tokens, parse_db)
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


def parse(tokens, parse_db=None):
  """
  digest tokens, then layout the digested blocks.
  """
  if parse_db is None:
    from cmake_format import parse_funs
    parse_db = parse_funs.get_parse_db()

  return consume_body(tokens, parse_db)


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


def dump_tree_upto(nodes, history, outfile=None, indent=None):
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

    if history[0] is node:
      # ANSI red
      outfile.write("\u001b[31m")
      if sys.version_info[0] < 3:
        outfile.write(repr(node).decode('utf-8'))
      else:
        outfile.write(repr(node))
      # ANSI reset
      outfile.write("\u001b[0m")
    else:
      if sys.version_info[0] < 3:
        outfile.write(repr(node).decode('utf-8'))
      else:
        outfile.write(repr(node))
    outfile.write('\n')

    if not hasattr(node, 'children'):
      continue

    subhistory = history[1:]
    if not subhistory:
      continue

    if idx + 1 == len(nodes):
      dump_tree_upto(node.children, subhistory, outfile, indent + '    ')
    else:
      dump_tree_upto(node.children, subhistory, outfile, indent + '│   ')


def tree_string(nodes, history=None):
  outfile = io.StringIO()
  if history:
    dump_tree_upto(nodes, history, outfile)
  else:
    dump_tree(nodes, outfile)
  return outfile.getvalue()


def has_nontoken_children(node):
  if not hasattr(node, 'children'):
    return False

  for child in node.children:
    if isinstance(child, TreeNode):
      return True

  return False


def dump_tree_for_test(nodes, outfile=None, indent=None, increment=None):
  """
  Print a tree of node objects for debugging purposes
  """
  if increment is None:
    increment = '    '

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
      dump_tree_for_test(node.children, outfile, indent + increment, increment)
      outfile.write(indent)
    outfile.write(']),\n')


def test_string(nodes, indent=None, increment=None):
  if indent is None:
    indent = ' ' * 10
  if increment is None:
    increment = '    '

  outfile = io.StringIO()
  dump_tree_for_test(nodes, outfile, indent, increment)
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
