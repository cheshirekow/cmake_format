# pylint: disable=too-many-lines
"""
Statement parser functions
"""

import importlib
import logging

from cmake_format import commands
from cmake_format import lexer
from cmake_format import parser
from cmake_format.parser import (
    consume_trailing_comment,
    consume_whitespace_and_comments,
    get_first_semantic_token,
    get_normalized_kwarg,
    get_tag,
    KwargBreaker,
    NodeType,
    parse_conditional,
    parse_kwarg,
    parse_pattern,
    parse_positionals,
    parse_shell_command,
    parse_standard,
    PositionalParser,
    should_break,
    StandardParser,
    TreeNode,
    WHITESPACE_TOKENS,
)

logger = logging.getLogger("cmake_format")


def split_legacy_spec(cmdspec):
  """
  Split a legacy specification object into pargs, kwargs, and flags
  """
  kwargs = {}
  for kwarg, subspec in cmdspec.items():
    if kwarg in cmdspec.flags:
      continue
    if kwarg in ("if", "elseif", "while"):
      subparser = parser.parse_conditional
    elif kwarg == "COMMAND":
      subparser = parser.parse_shell_command
    elif isinstance(subspec, parser.IMPLICIT_PARG_TYPES):
      subparser = parser.PositionalParser(subspec, [])
    elif isinstance(subspec, (commands.CommandSpec)):
      subparser = get_legacy_parse(subspec)
    else:
      raise ValueError("Unexpected kwarg spec of type {}"
                       .format(type(subspec)))
    kwargs[kwarg] = subparser

  return cmdspec.pargs, kwargs, cmdspec.flags


def get_legacy_parse(cmdspec):
  """
  Construct a parse tree from a legacy command specification
  """
  pargs, kwargs, flags = split_legacy_spec(cmdspec)
  return parser.StandardParser(pargs, kwargs, flags)


def parse_set(tokens, breakstack):
  """
  ::

    set(<variable> <value>
        [[CACHE <type> <docstring> [FORCE]] | PARENT_SCOPE])

  :see: https://cmake.org/cmake/help/v3.0/command/set.html?
  """
  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  kwargs = {
      "CACHE": PositionalParser(3, flags=["FORCE"])
  }
  flags = ["PARENT_SCOPE"]
  kwarg_breakstack = breakstack + [KwargBreaker(list(kwargs.keys()) + flags)]
  positional_breakstack = breakstack + [KwargBreaker(list(kwargs.keys()))]

  ntokens = len(tokens)
  subtree = parse_positionals(tokens, 1, flags, positional_breakstack)
  assert len(tokens) < ntokens
  tree.children.append(subtree)

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
      if not get_tag(tokens[0]) in ("sort", "sortable"):
        child = TreeNode(NodeType.COMMENT)
        tree.children.append(child)
        child.children.append(tokens.pop(0))
        continue

    ntokens = len(tokens)
    # NOTE(josh): each flag is also stored in kwargs as with a positional parser
    # of size zero. This is a legacy thing that should be removed, but for now
    # just make sure we check flags first.
    word = get_normalized_kwarg(tokens[0])
    if word == "CACHE":
      subtree = parse_kwarg(tokens, word, kwargs[word], kwarg_breakstack)
    elif word == "PARENT_SCOPE":
      subtree = parse_positionals(tokens, '+', ["PARENT_SCOPE"],
                                  positional_breakstack)
    else:
      subtree = parse_positionals(tokens, '+', [], kwarg_breakstack)

    assert len(tokens) < ntokens
    tree.children.append(subtree)
  return tree


SUBMODULE_NAMES = [
    "add_executable",
    "add_library",
    "add_xxx",
    "external_project",
    "fetch_content",
    "file",
    "install"
]


def get_parse_db():
  """
  Returns a dictionary mapping statement name to parse functor for that
  statement.
  """

  parse_db = {}

  for subname in SUBMODULE_NAMES:
    submodule = importlib.import_module("cmake_format.parse_funs." + subname)
    submodule.populate_db(parse_db)

  parse_db["set"] = parse_set

  for key in ("if", "else", "elseif", "endif", "while", "endwhile"):
    parse_db[key] = parser.parse_conditional

  return parse_db
