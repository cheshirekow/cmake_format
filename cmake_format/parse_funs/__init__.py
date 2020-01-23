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
    ConditionalGroupNode, StandardParser, StandardParser2
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

logger = logging.getLogger(__name__)


def split_legacy_spec(cmdspec):
  """
  Split a legacy specification object into pargs, kwargs, and flags
  """
  kwargs = {}
  for kwarg, subspec in cmdspec.kwargs.items():
    if kwarg in ("if", "elseif", "while"):
      subparser = ConditionalGroupNode.parse
    elif kwarg == "COMMAND":
      subparser = ShellCommandNode.parse
    elif isinstance(subspec, (commands.CommandSpec)):
      subparser = get_legacy_parse(subspec)
    else:
      raise ValueError("Unexpected kwarg spec of type {}"
                       .format(type(subspec)))
    kwargs[kwarg] = subparser

  return cmdspec.pargs, kwargs


def get_legacy_parse(cmdspec):
  """
  Construct a parse tree from a legacy command specification
  """
  pspec, kwargs = split_legacy_spec(cmdspec)
  return StandardParser2(pspec, kwargs)


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
    "list",
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
      "if", "else", "elseif", "endif", "while", "endwhile"):
    parse_db[key] = ConditionalGroupNode.parse

  for key in ("function", "macro"):
    parse_db[key] = StandardParser("1+")

  for key in ("endfunction", "endmacro"):
    parse_db[key] = StandardParser("?")

  return parse_db
