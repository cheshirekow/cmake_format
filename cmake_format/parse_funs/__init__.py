# pylint: disable=too-many-lines
"""
Statement parser functions
"""

import importlib
import logging

from cmake_format import commands
from cmake_format import lexer
from cmake_format.parse.additional_nodes import ShellCommandNode
from cmake_format.parse.argument_nodes import (
    ConditionalGroupNode, StandardParser
)
from cmake_format.parse.common import NodeType, KwargBreaker, TreeNode
from cmake_format.parse.util import (
    IMPLICIT_PARG_TYPES,
    WHITESPACE_TOKENS,
    get_first_semantic_token,
    get_normalized_kwarg,
    get_tag,
    should_break,
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
      subparser = ConditionalGroupNode.parse
    elif kwarg == "COMMAND":
      subparser = ShellCommandNode.parse
    elif isinstance(subspec, IMPLICIT_PARG_TYPES):
      subparser = StandardParser(subspec)
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
  return StandardParser(pargs, kwargs, flags)


SUBMODULE_NAMES = [
    "add_executable",
    "add_library",
    "add_xxx",
    "deprecated",
    "break",
    "external_project",
    "fetch_content",
    "foreach",
    "file",
    "install",
    "miscellaneous",
    "random",
    "set",
    "set_target_properties"
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

  for key in (
      "if", "else", "elseif", "endif", "while", "endwhile",
      "function", "endfunction", "macro", "endmacro"):
    parse_db[key] = ConditionalGroupNode.parse

  return parse_db
