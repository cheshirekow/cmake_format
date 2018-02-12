from __future__ import print_function

from cmake_format import lexer


def make_enum_map(names):
  """
  Construct the inverse map from enum values to names
  """
  return {globals()[name]: name for name in names}


# Token sequence types
STATEMENT = 0
WHITESPACE = 1
COMMENT = 2

kSeqTypeToStr = make_enum_map(["STATEMENT", "WHITESPACE", "COMMENT"])

WHITESPACE_TOKENS = [lexer.WHITESPACE,
                     lexer.NEWLINE]

COMMENT_TOKENS = [lexer.COMMENT,
                  lexer.FORMAT_OFF,
                  lexer.FORMAT_ON]


class TokenSequence(object):
  """
  A sequence of tokens composing one of:
  1. a cmake statement
  2. a cmake comment
  3. some whitespace
  """

  def __init__(self, seq_type, tokens):
    self.type = seq_type
    self.tokens = tokens

  def __repr__(self):
    return ("{}: {}:{}"
            .format(kSeqTypeToStr.get(self.type),
                    self.tokens[0].line, self.tokens[0].col))


def consume_whitespace(tokens):
  """
  Consume sequential whitespace, removing tokens from the iniput list and
  returning a whitespace TokenSequence
  """

  whitespace_tokens = []
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    whitespace_tokens.append(tokens.pop(0))
  return TokenSequence(WHITESPACE, whitespace_tokens)


def consume_comment(tokens):
  """
  Consume sequential comment lines, removing tokens from the input list and
  returning a comment TokenSequence
  """

  comment_tokens = []
  while tokens and tokens[0].type in COMMENT_TOKENS:
    comment_tokens.append(tokens.pop(0))
    # pylint: disable=bad-continuation
    if (len(tokens) > 2
        and tokens[0].type == lexer.NEWLINE
        and tokens[1].type in COMMENT_TOKENS
        ):
      comment_tokens.append(tokens.pop(0))
  return TokenSequence(COMMENT, comment_tokens)


def consume_statement(tokens):
  """
  Consume a complete statement, removint tokens from the input list and
  returning a statement TokenSequence
  """
  stmt_tokens = [tokens.pop(0)]
  while tokens[0].type in WHITESPACE_TOKENS:
    stmt_tokens.append(tokens.pop(0))

  assert tokens[0].type == lexer.LEFT_PAREN, \
      ("Unexpected {} token at {}:{}, expecting l-paren, got {}"
       .format(lexer.token_type_to_str(tokens[0].type), tokens[0].line,
               tokens[0].col, tokens[0].content))

  stmt_tokens.append(tokens.pop(0))
  paren_count = 1

  while tokens and paren_count > 0:
    if tokens[0].type == lexer.LEFT_PAREN:
      paren_count += 1
    elif tokens[0].type == lexer.RIGHT_PAREN:
      paren_count -= 1
    stmt_tokens.append(tokens.pop(0))

  assert paren_count == 0, \
      ("Missing terminating r-paren for statement starting at {}:{}\n"
       .format(stmt_tokens[0].line, stmt_tokens[0].col))

  while tokens:
    if tokens[0].type in [lexer.COMMENT,
                          lexer.BRACKET_COMMENT,
                          lexer.WHITESPACE]:
      stmt_tokens.append(tokens.pop(0))
    else:
      break

  while (len(tokens) > 2
         and tokens[0].type == lexer.NEWLINE
         and tokens[1].type == lexer.WHITESPACE
         and tokens[2].type in (lexer.COMMENT, lexer.BRACKET_COMMENT)):
    stmt_tokens.append(tokens.pop(0))
    stmt_tokens.append(tokens.pop(0))
    stmt_tokens.append(tokens.pop(0))

  return TokenSequence(STATEMENT, stmt_tokens)


def digest_tokens(tokens):
  """
  Consume tokens and output collections of tokens (as TokenSequence) objects
  representing one of the following classes:

  1. whitespace
  2. comment
  3. statement
  """

  tokens = list(tokens)
  tok_seqs = []

  while tokens:
    if tokens[0].type in WHITESPACE_TOKENS:
      tok_seqs.append(consume_whitespace(tokens))
    elif tokens[0].type in COMMENT_TOKENS:
      tok_seqs.append(consume_comment(tokens))
    elif tokens[0].type == lexer.BRACKET_COMMENT:
      tok_seqs.append(TokenSequence(COMMENT, [tokens.pop(0)]))
    elif tokens[0].type == lexer.WORD:
      tok_seqs.append(consume_statement(tokens))
    else:
      assert False, ("Unexpected token of type {} at {}:{}"
                     .format(lexer.token_type_to_str(tokens[0].type),
                             tokens[0].line, tokens[0].col))

  return tok_seqs


def dump_digest(tok_seqs):
  """
  Print a series of token_sequences for debugging purposes
  """
  for tok_seq in tok_seqs:
    print(tok_seq)


# Node Types
BLOCK_NODE = 0
COMMENT_NODE = 1
WHITESPACE_NODE = 2
STATEMENT_NODE = 3

kNodeTypeToStr = make_enum_map(["BLOCK_NODE", "COMMENT_NODE",
                                "WHITESPACE_NODE", "STATEMENT_NODE"])

# Block Node subtypes
ROOT = 4
IF_BLOCK = 5
WHILE = 6
FOREACH = 7
FUNCTION_DEF = 8
MACRO_DEF = 9

kBlockTypeToStr = make_enum_map(["ROOT", "IF_BLOCK", "WHILE", "FOREACH",
                                 "FUNCTION_DEF", "MACRO_DEF"])


class TreeNode(object):
  """
  A node in the full-syntax-tree.
  """

  def __init__(self, node_type):
    self.node_type = node_type

  def get_location(self):
    """
    Return the (line, col) of the first token in the subtree rooted at this
    node.
    """
    if hasattr(self, 'content'):
      token = getattr(self, 'content').tokens[0]
      return token.line, token.col
    elif hasattr(self, 'children') and getattr(self, 'children'):
      return getattr(self, 'children')[0].get_location()

    return -1, -1

  def __repr__(self):
    line, col = self.get_location()
    return '{}:{}:{}'.format(kNodeTypeToStr.get(self.node_type),
                             line, col)


class Block(TreeNode):
  """
  A node with children but no content. A block node is used to represent the top
  level of a listfile, as well as any kind of logical "scope" constructs like
  conditional statements or loops. In the case of a scope-block the children
  of this node are the statements that define the scope (if, elseif,
  else, endif) and not the statements within the body of the scope.
  """

  def __init__(self, block_type, children=None):
    super(Block, self).__init__(BLOCK_NODE)
    self.block_type = block_type
    self.children = children if children else []

  def __repr__(self):
    line, col = self.get_location()
    return '{}({}):{}:{}'.format(kNodeTypeToStr.get(self.node_type),
                                 kBlockTypeToStr.get(self.block_type),
                                 line, col)


class Comment(TreeNode):
  """
  Has a ``content`` field containing a TokenSequence of comment tokens.
  Represents a continuous sequence of comment lines up to the first blank line
  or cmake statment. The ``content`` contains the full TokenSequence, including
  lexer.NEWLINE objects between each comment line.
  """

  def __init__(self, content=None):
    super(Comment, self).__init__(COMMENT_NODE)
    self.content = content


class Whitespace(TreeNode):
  """
  Has a ``content`` field containing a TokenSequence of whitespace tokens.
  Represents a continuous sequence of whitespace (either lexer.Newline or
  lexer.Whitespace) between a comment or a cmake statement. Note that
  ``content`` contains the full TokenSequence, including trailing whitespace
  or multiple newlines.
  """

  def __init__(self, content=None):
    super(Whitespace, self).__init__(WHITESPACE_NODE)
    self.content = content

  def count_newlines(self):
    newline_count = 0
    for token in self.content.tokens:
      newline_count += token.content.count('\n')
    return newline_count


class Argument(object):
  """
  A single semantic argument of a cmake statement (command/function-call). It
  is composed of nominally one token, but may also be associated with a list
  of comment strings which are digested stripped out of comment tokens.
  """

  def __init__(self, token, comments=None):
    self.tokens = [token]
    self.comments = comments if comments else []
    self.contents = token.content


class Statement(TreeNode):
  """
  A single cmake statement. A statement has at most one child (stored in
  ``children``). Note that some statements are "simple" function calls
  while other statements (like ``if``, or ``while``) open a new logical block.
  Simple statements have no children and logical block statements have one
  child.

  The arguments of a statement are stored in the ``content`` list of this
  node as a sequence of ``Argument`` objects.
  """

  def __init__(self, content=None, child=None):
    super(Statement, self).__init__(STATEMENT_NODE)
    self.content = content
    self.children = list(child) if child else []
    self.prefix_tokens = []
    self.postfix_tokens = []

    tokens = list(content.tokens)
    assert tokens[0].type == lexer.WORD
    self.prefix_tokens.append(tokens.pop(0))
    self.name = self.prefix_tokens[0].content
    self.body = []
    while tokens and tokens[0].type != lexer.LEFT_PAREN:
      self.prefix_tokens.append(tokens.pop(0))
    assert tokens
    self.prefix_tokens.append(tokens.pop(0))

    paren_count = 1

    while tokens and paren_count > 0:
      token = tokens.pop(0)
      if token.type in WHITESPACE_TOKENS:
        if self.body:
          self.body[-1].tokens.append(token)
        else:
          self.prefix_tokens.append(token)
      elif token.type == lexer.COMMENT:
        assert self.body
        self.body[-1].tokens.append(token)
        self.body[-1].comments.append(token.content)
      elif token.type == lexer.LEFT_PAREN:
        paren_count += 1
        self.body.append(Argument(token))
      elif token.type == lexer.RIGHT_PAREN:
        paren_count -= 1
        if paren_count > 0:
          self.body.append(Argument(token))
        else:
          self.postfix_tokens.append(token)
      else:
        self.body.append(Argument(token))
    self.comment = ""
    while tokens:
      self.postfix_tokens.append(tokens.pop(0))
      if self.postfix_tokens[-1].type == lexer.COMMENT:
        if self.comment:
          self.comment += "\n"
        self.comment += self.postfix_tokens[-1].content.strip().lstrip('#')


def construct_fst(token_seqs):
  """
  Given a list of token sequences (the output of digest_tokens), construct the
  Full Syntax Tree
  """

  # TODO(josh): figure out a cleaner way to deal with this switch/case logic
  # pylint: disable=too-many-statements
  block_stack = [Block(ROOT)]
  token_seqs = list(token_seqs)
  while token_seqs:
    tok_seq = token_seqs.pop(0)
    if tok_seq.type == COMMENT:
      block_stack[-1].children.append(Comment(tok_seq))
    elif tok_seq.type == WHITESPACE:
      block_stack[-1].children.append(Whitespace(tok_seq))
    elif tok_seq.type == STATEMENT:
      if tok_seq.tokens[0].content.lower() == 'if':
        block = Block(IF_BLOCK)
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(block)
        block.children.append(stmt)
        block_stack.append(block)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() in ['elseif', 'else']:
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == IF_BLOCK
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() == 'endif':
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == IF_BLOCK
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.pop(-1)
      elif tok_seq.tokens[0].content.lower() == 'while':
        block = Block(WHILE)
        stmt = Statement(tok_seq)
        block.children.append(stmt)
        block_stack.append(block)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() == 'endwhile':
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == WHILE
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.pop(-1)
      elif tok_seq.tokens[0].content.lower() == 'foreach':
        block = Block(FOREACH)
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(block)
        block.children.append(stmt)
        block_stack.append(block)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() == 'endforeach':
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == FOREACH
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.pop(-1)
      elif tok_seq.tokens[0].content.lower() == 'function':
        block = Block(FUNCTION_DEF)
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(block)
        block.children.append(stmt)
        block_stack.append(block)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() == 'endfunction':
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == FUNCTION_DEF
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.pop(-1)
      elif tok_seq.tokens[0].content.lower() == 'macro':
        block = Block(MACRO_DEF)
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(block)
        block.children.append(stmt)
        block_stack.append(block)
        block_stack.append(stmt)
      elif tok_seq.tokens[0].content.lower() == 'endmacro':
        assert block_stack and block_stack.pop(-1)
        assert block_stack and block_stack[-1].block_type == MACRO_DEF
        stmt = Statement(tok_seq)
        block_stack[-1].children.append(stmt)
        block_stack.pop(-1)
      else:
        block_stack[-1].children.append(Statement(tok_seq))

  if len(block_stack) != 1:
    for block in block_stack[::-1]:
      if block.node_type == BLOCK_NODE:
        raise AssertionError("Unclosed block of type: {} opened at {}:{}"
                             .format(kBlockTypeToStr.get(block.block_type),
                                     block.children[0].line,
                                     block.children[0].col))

    raise AssertionError('Unclosed node of type: {}'
                         .format(block_stack[-1].node_type))

  return block_stack[0]


def dump_fst(node, depth=0):
  print('{}{}'.format('  ' * depth, node))
  for child in getattr(node, 'children', []):
    dump_fst(child, depth + 1)


def main():
  """
  Dump digested tokens or full-syntax-tree to stdout for debugging purposes.
  """
  import argparse
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('infile')
  subparsers = parser.add_subparsers(dest='command')
  subparsers.add_parser('dump-digest')
  subparsers.add_parser('dump-tree')

  args = parser.parse_args()
  with open(args.infile, 'r') as infile:
    tokens = lexer.tokenize(infile.read())
    tok_seqs = digest_tokens(tokens)
    fst = construct_fst(tok_seqs)

  if args.command == 'dump-digest':
    for seq in tok_seqs:
      print(seq)
  elif args.command == 'dump-tree':
    dump_fst(fst)
  else:
    assert False, "Unkown command {}".format(args.command)


if __name__ == '__main__':
  main()
