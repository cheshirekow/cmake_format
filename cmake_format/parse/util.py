# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import sys

from cmake_format import lexer

logger = logging.getLogger(__name__)

if sys.version_info[0] < 3:
  STRING_TYPES = (str, unicode)
else:
  STRING_TYPES = (str,)

IMPLICIT_PARG_TYPES = STRING_TYPES + (int,)

WHITESPACE_TOKENS = (lexer.TokenType.WHITESPACE,
                     lexer.TokenType.NEWLINE)

# TODO(josh): Don't include FORMAT_OFF and FORMAT_ON in comment tokens. They
# wont get reflowed within a comment block so there is no reason to parse them
# as such.
COMMENT_TOKENS = (lexer.TokenType.COMMENT,)
ONOFF_TOKENS = (lexer.TokenType.FORMAT_ON,
                lexer.TokenType.FORMAT_OFF)

ALL_COMMENT_TOKENS = (
    lexer.TokenType.COMMENT,
    lexer.TokenType.BRACKET_COMMENT,
    lexer.TokenType.FORMAT_ON,
    lexer.TokenType.FORMAT_OFF
)

NON_SEMANTIC_TOKENS = ALL_COMMENT_TOKENS + WHITESPACE_TOKENS


def is_whitespace_token(token):
  return token.type in WHITESPACE_TOKENS


def is_comment_token(token):
  return token.type in COMMENT_TOKENS


def is_syntactic_token(token):
  """Return true for everything that isn't whitespace"""
  if token.type in WHITESPACE_TOKENS:
    return False
  return True


def is_semantic_token(token):
  """Return true for everything that isnt' whitespace or a comment"""
  if token.type in NON_SEMANTIC_TOKENS:
    return False
  return True


def is_variable_dereference(token):
  return token.type is lexer.TokenType.DEREF


def is_valid_trailing_comment(token):
  """
  Return true if the token is a valid trailing comment
  """
  return (token.type in (lexer.TokenType.COMMENT,
                         lexer.TokenType.BRACKET_COMMENT) and
          not comment_is_tag(token))


def are_column_aligned(token_a, token_b):
  """
  Return true if both tokens are on the same column.
  """
  return token_a.begin.col == token_b.begin.col


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


def comment_is_tag(token):
  """
  Return true if the comment token has one of the tag-forms:

  # cmake-format: <tag>
  # cmf: <tag>
  #[[cmake-format:<tag>]]
  #[[cmf:<tag>]]
  """
  return get_tag(token) is not None


def pargs_are_full(npargs, nconsumed):
  if isinstance(npargs, int):
    return nconsumed >= npargs

  assert isinstance(npargs, STRING_TYPES), (
      "Unexpected npargs type {}".format(type(npargs)))

  if npargs == "?":
    return nconsumed >= 1

  if npargs in ("*", "+"):
    return False

  if npargs.endswith("+"):
    try:
      _ = int(npargs[:-1])
    except ValueError:
      raise ValueError("Unexepected npargs {}".format(npargs))
  return False


def npargs_is_exact(npargs):
  """
  Return true if npargs has an exact specification
  """
  return isinstance(npargs, int)


def get_min_npargs(npargs):
  """If the npargs specification string indicates a minimum number of arguments
     then return that value."""

  if npargs is None:
    return 0

  if isinstance(npargs, int):
    return npargs

  if npargs in ("*", "?"):
    return 0

  if npargs == "+":
    return 1

  if npargs.endswith("+"):
    return int(npargs[:-1])

  raise ValueError("Unexpected npargs {}".format(npargs))


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


def iter_syntactic_tokens(tokens):
  """
  Return a generator over the list of tokens yielding only those that are
  not whitespace
  """
  skip_tokens = (lexer.TokenType.WHITESPACE,
                 lexer.TokenType.NEWLINE)

  for token in tokens:
    if token.type in skip_tokens:
      continue
    yield token


def get_next_syntactic_token(tokens):
  """
  return the first non-whitespace token in the list
  """
  for token in iter_syntactic_tokens(tokens):
    return token
  return None


def iter_semantic_tokens(tokens):
  """
  Return a generator over the list of tokens yielding only those that
  have semantic meaning
  """

  for token in tokens:
    if is_semantic_token(token):
      yield token


def get_nth_semantic_token(tokens, nth):
  idx = 0
  for token in iter_semantic_tokens(tokens):
    if idx == nth:
      return token
    idx += 1
  return None


def get_first_semantic_token(tokens):
  """
  Return the first token with semantic meaning
  """
  return get_nth_semantic_token(tokens, 0)
