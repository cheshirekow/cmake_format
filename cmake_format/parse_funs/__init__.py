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


def parse_install_targets_sub(tokens, breakstack):
  """
    Parse the inner kwargs of an ``install(TARGETS)`` command. This is common
    logic for ARCHIVE, LIBRARY, RUNTIME, etc.
  :see: https://cmake.org/cmake/help/v3.14/command/install.html#targets
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "DESTINATION": PositionalParser(1),
          "PERMISSIONS": PositionalParser('+'),
          "CONFIGURATIONS": PositionalParser('+'),
          "COMPONENT": PositionalParser(1),
          "NAMELINK_COMPONENT": PositionalParser(1),
      },
      flags=[
          "OPTIONAL",
          "EXCLUDE_FROM_ALL",
          "NAMELINK_ONLY",
          "NAMELINK_SKIP"
      ],
      breakstack=breakstack)


def parse_install_targets(tokens, breakstack):
  """
  ::

    install(TARGETS targets... [EXPORT <export-name>]
            [[ARCHIVE|LIBRARY|RUNTIME|OBJECTS|FRAMEWORK|BUNDLE|
              PRIVATE_HEADER|PUBLIC_HEADER|RESOURCE]
             [DESTINATION <dir>]
             [PERMISSIONS permissions...]
             [CONFIGURATIONS [Debug|Release|...]]
             [COMPONENT <component>]
             [NAMELINK_COMPONENT <component>]
             [OPTIONAL] [EXCLUDE_FROM_ALL]
             [NAMELINK_ONLY|NAMELINK_SKIP]
            ] [...]
            [INCLUDES DESTINATION [<dir> ...]]
            )

  :see: https://cmake.org/cmake/help/v3.14/command/install.html#targets
  """
  kwargs = {
      "TARGETS": PositionalParser('+'),
      "EXPORT": PositionalParser(1),
      "INCLUDES": PositionalParser('+', flags=["DESTINATION"])
  }
  for subkey in ("ARCHIVE", "LIBRARY", "RUNTIME", "OBJECTS", "FRAMEWORK",
                 "BUNDLE", "PRIVATE_HEADER", "PUBLIC_HEADER", "RESOURCE"):
    kwargs[subkey] = parse_install_targets_sub

  return parse_standard(
      tokens,
      npargs='*',
      kwargs=kwargs,
      flags=[],
      breakstack=breakstack)


def parse_install_files(tokens, breakstack):
  """
  ::
    install(<FILES|PROGRAMS> files...
            TYPE <type> | DESTINATION <dir>
            [PERMISSIONS permissions...]
            [CONFIGURATIONS [Debug|Release|...]]
            [COMPONENT <component>]
            [RENAME <name>] [OPTIONAL] [EXCLUDE_FROM_ALL])

  :see: https://cmake.org/cmake/help/v3.14/command/install.html#files
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "FILES": PositionalParser('+'),
          "PROGRAMS": PositionalParser('+'),
          "TYPE": PositionalParser(1),
          "DESTINATION": PositionalParser(1),
          "PERMISSIONS": PositionalParser('+'),
          "CONFIGURATIONS": PositionalParser('+'),
          "COMPONENT": PositionalParser(1),
          "RENAME": PositionalParser(1),
      },
      flags=[
          "OPTIONAL",
          "EXCLUDE_FROM_ALL",
      ],
      breakstack=breakstack)


def parse_install_directory(tokens, breakstack):
  """
  ::

    install(DIRECTORY dirs...
            TYPE <type> | DESTINATION <dir>
            [FILE_PERMISSIONS permissions...]
            [DIRECTORY_PERMISSIONS permissions...]
            [USE_SOURCE_PERMISSIONS] [OPTIONAL] [MESSAGE_NEVER]
            [CONFIGURATIONS [Debug|Release|...]]
            [COMPONENT <component>] [EXCLUDE_FROM_ALL]
            [FILES_MATCHING]
            [[PATTERN <pattern> | REGEX <regex>]
             [EXCLUDE] [PERMISSIONS permissions...]] [...])

  :see: https://cmake.org/cmake/help/v3.14/command/install.html#directory
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "DIRECTORY": PositionalParser('+'),
          "TYPE": PositionalParser(1),
          "DESTINATION": PositionalParser(1),
          "FILE_PERMISSIONS": PositionalParser('+'),
          "DIRECTORY_PERMISSIONS": PositionalParser('+'),
          "CONFIGURATIONS": PositionalParser('+'),
          "COMPONENT": PositionalParser(1),
          "RENAME": PositionalParser(1),
          "PATTERN": parse_pattern,
          "REGEX": parse_pattern,
      },
      flags=[
          "USER_SOURCE_PERMISSIONS",
          "OPTIONAL",
          "MESSAGE_NEVER",
          "FILES_MATCHING",
      ],
      breakstack=breakstack)


def parse_install_script(tokens, breakstack):
  """
  ::

    install([[SCRIPT <file>] [CODE <code>]]
            [COMPONENT <component>] [EXCLUDE_FROM_ALL] [...])

  :see: https://cmake.org/cmake/help/v3.14/command/install.html#custom-installation-logic
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "SCRIPT": PositionalParser(1),
          "CODE": PositionalParser(1),
          "COMPONENT": PositionalParser(1),
      },
      flags=[
          "EXCLUDE_FROM_ALL"
      ],
      breakstack=breakstack)


def parse_install_export(tokens, breakstack):
  """
  ::

    install(EXPORT <export-name> DESTINATION <dir>
            [NAMESPACE <namespace>] [[FILE <name>.cmake]|
            [PERMISSIONS permissions...]
            [CONFIGURATIONS [Debug|Release|...]]
            [EXPORT_LINK_INTERFACE_LIBRARIES]
            [COMPONENT <component>]
            [EXCLUDE_FROM_ALL])

  :see: https://cmake.org/cmake/help/v3.14/command/install.html#installing-exports
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "EXPORT": PositionalParser(1),
          "DESTINATION": PositionalParser(1),
          "NAMESPACE": PositionalParser(1),
          "FILE": PositionalParser(1),
          "PERMISSIONS": PositionalParser('+'),
          "CONFIGURATIONS": PositionalParser('+'),
          "COMPONENT": PositionalParser(1),
      },
      flags=[
          "EXCLUDE_FROM_ALL"
      ],
      breakstack=breakstack)


def parse_install(tokens, breakstack):
  """
  The ``install()`` command has multiple different forms, implemented
  by different functions. The forms are indicated by the first token
  and are:

  * TARGETS
  * FILES
  * DIRECTORY
  * SCRIPT
  * CODE
  * EXPORT

  :see: https://cmake.org/cmake/help/v3.0/command/install.html
  """

  descriminator_token = get_first_semantic_token(tokens)
  if descriminator_token is None:
    logger.warning("Invalid install() command at %s", tokens[0].get_location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  descriminator = descriminator_token.spelling.upper()
  parsemap = {
      "TARGETS": parse_install_targets,
      "FILES": parse_install_files,
      "PROGRAMS": parse_install_files,
      "DIRECTORY": parse_install_directory,
      "SCRIPT": parse_install_script,
      "CODE": parse_install_script,
      "EXPORT": parse_install_export
  }
  if descriminator not in parsemap:
    logger.warning("Invalid install form \"%s\" at %s", descriminator,
                   tokens[0].location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  return parsemap[descriminator](tokens, breakstack)


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
    'add_xxx',
    'external_project',
    'fetch_content',
    'file'
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

  parse_db["install"] = parse_install
  parse_db["set"] = parse_set

  for key in ("if", "else", "elseif", "endif", "while", "endwhile"):
    parse_db[key] = parser.parse_conditional

  return parse_db
