from __future__ import print_function
from __future__ import unicode_literals

import enum
import logging
import re

logger = logging.getLogger(__name__)


class TokenType(enum.IntEnum):

  LSQ_BRACKET = 0
  RSQ_BRACKET = 1
  LA_BRACKET = 2
  RA_BRACKET = 3
  PIPE = 4
  BIGNAME = 5
  SMALLNAME = 6
  ELLIPSIS = 7
  WHITESPACE = 8
  LPAREN = 9
  RPAREN = 10


class SourceLocation(tuple):
  """
  Named tuple of (line, col, offset)
  """

  # def __init__(self, line, col, offset):
  #   super(SourceLocation, self).__init__((line, col, offset))

  @property
  def line(self):
    return self[0]

  @property
  def col(self):
    return self[1]

  @property
  def offset(self):
    return self[2]

  def __repr__(self):
    return '{}:{}'.format(self.line, self.col)


class Token(object):
  """
  Lexical unit of a listfile.
  """

  def __init__(self, tok_type, spelling, index, begin, end):
    self.type = tok_type
    self.spelling = spelling
    self.index = index
    self.begin = begin
    self.end = end

  @property
  def content(self):
    return self.spelling

  # TODO(josh): get rid of this? Is it used or did I accidentally add it when
  # I meant to add get_location()? Or should this be a property?
  def location(self):
    return self.begin

  def get_location(self):
    return self.begin

  def count_newlines(self):
    return self.spelling.count('\n')

  def __repr__(self):
    """A string representation of this token."""
    return ("Token({0}{2}:{3} {1})").format(
        repr(self.spelling), self.type.name, *self.begin)


def tokenize_inner(contents):
  """
  Scan a string and return a list of Token objects representing the contents
  of the cmake listfile.
  """

  # Regexes are in priority order. Changing the order may alter the
  # behavior of the lexer
  scanner = re.Scanner([
      # Optional group brackets
      (r"\[", lambda s, t: (TokenType.LSQ_BRACKET, t)),
      (r"\]", lambda s, t: (TokenType.RSQ_BRACKET, t)),
      # Mandatory group brackets
      ("<", lambda s, t: (TokenType.LA_BRACKET, t)),
      (">", lambda s, t: (TokenType.RA_BRACKET, t)),
      # Parenthesis
      (r"\(", lambda s, t: (TokenType.LPAREN, t)),
      (r"\)", lambda s, t: (TokenType.RPAREN, t)),
      # Pipe character
      (r"\|", lambda s, t: (TokenType.PIPE, t)),
      # uppercase name
      (r"[A-Z0-9_]+", lambda s, t: (TokenType.BIGNAME, t)),
      # lowercase name
      (r"[a-z0-9_\-]+", lambda s, t: (TokenType.SMALLNAME, t)),
      # ellipsis
      (r"\.\.\.", lambda s, t: (TokenType.ELLIPSIS, t)),
      # whitespace
      (r"\s+", lambda s, t: (TokenType.WHITESPACE, t)),
  ], re.DOTALL)

  tokens, remainder = scanner.scan(contents)
  if remainder:
    raise ValueError("Unparsed tokens: {}".format(remainder))
  return tokens


def annotate_tokens(tokens):
  """
  Add source location and index information to tokens
  """

  # Now add line, column, and serial number to token objects. We get lineno
  # by maintaining a running count of newline characters encountered among
  # tokens so far, and column count by splitting the most recent token on
  # it's right most newline. Note that line and numbers are 1-indexed to match
  # up with editors but column numbers are zero indexed because its fun to be
  # inconsistent.
  lineno = 1
  col = 0
  offset = 0
  tokens_return = []
  for tok_index, (tok_type, spelling) in enumerate(tokens):
    begin = SourceLocation((lineno, col, offset))
    newlines = spelling.count('\n')
    lineno += newlines
    if newlines:
      col = len(spelling.rsplit('\n', 1)[1])
    else:
      col += len(spelling)

    offset += len(bytearray(spelling, 'utf-8'))
    tokens_return.append(Token(
        tok_type=tok_type,
        spelling=spelling,
        index=tok_index,
        begin=begin,
        end=SourceLocation((lineno, col, offset))
    ))
  return tokens_return


def tokenize(content):
  if "(" not in content or ")" not in content:
    raise ValueError("Missing parenthesis")

  tokens = tokenize_inner(content)
  return annotate_tokens(tokens)


def main():
  """
  Dump tokenized usage text for debugging
  """
  import argparse
  import io
  import os
  import sys

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('infile')
  args = parser.parse_args()

  infile_arg = args.infile
  if args.infile == "-":
    infile_arg = os.dup(sys.stdin.fileno())

  with io.open(infile_arg, 'r') as infile:
    tokens = tokenize(infile.read())
  print('\n'.join(str(x) for x in tokens))


if __name__ == '__main__':
  main()
