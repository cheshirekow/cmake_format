# pylint: disable=too-many-lines
"""
Statement parser functions
"""

import logging

from cmake_format import commands
from cmake_format import lexer
from cmake_format import parser
from cmake_format.parser import (
    consume_trailing_comment,
    get_normalized_kwarg,
    get_tag,
    KwargBreaker,
    NodeType,
    parse_conditional,
    parse_kwarg,
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


def parse_add_library(tokens, breakstack):
  """
  ::

    add_library(<name> [STATIC | SHARED | MODULE]
               [EXCLUDE_FROM_ALL]
               source1 [source2 ...])

  :see: https://cmake.org/cmake/help/v3.0/command/add_library.html
  """
  # pylint: disable=too-many-statements

  parsing_name = 1
  parsing_type = 2
  parsing_flag = 3
  parsing_sources = 4

  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  sortable = True
  state_ = parsing_name
  parg_group = None
  src_group = None
  active_depth = tree

  while tokens:
    # This parse function breakson the first right paren, since parenthetical
    # groups are not allowed. A parenthesis might exist in a filename, but
    # if so that filename should be quoted so it wont show up as a RIGHT_PAREN
    # token.
    if tokens[0].type is lexer.TokenType.RIGHT_PAREN:
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      active_depth.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      if (state_ > parsing_name and
          get_tag(tokens[0]) in ("unsort", "unsortable")):
        sortable = False
      child = TreeNode(NodeType.COMMENT)
      active_depth.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    if state_ is parsing_name:
      token = tokens.pop(0)
      parg_group = TreeNode(NodeType.PARGGROUP)
      active_depth = parg_group
      tree.children.append(parg_group)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_type:
      if get_normalized_kwarg(tokens[0]) in ("STATIC", "SHARED", "MODULE"):
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_flag:
      if get_normalized_kwarg(tokens[0]) == "EXCLUDE_FROM_ALL":
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      state_ += 1
      src_group = TreeNode(NodeType.PARGGROUP, sortable=sortable)
      active_depth = src_group
      tree.children.append(src_group)
    elif state_ is parsing_sources:
      token = tokens.pop(0)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      src_group.children.append(child)

      if only_comments_and_whitespace_remain(tokens, breakstack):
        active_depth = tree

  return tree



def parse_add_executable(tokens, breakstack):
  """
  ::

    add_executable(<name> [WIN32] [MACOSX_BUNDLE]
               [EXCLUDE_FROM_ALL]
               [source1] [source2 ...])

  :see: https://cmake.org/cmake/help/latest/command/add_executable.html#command:add_executable
  """
  # pylint: disable=too-many-statements

  parsing_name = 1
  parsing_flags = 2
  parsing_sources = 3

  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  sortable = True
  state_ = parsing_name
  parg_group = None
  src_group = None
  active_depth = tree

  while tokens:
    # This parse function breaks on the first right paren, since parenthetical
    # groups are not allowed. A parenthesis might exist in a filename, but
    # if so that filename should be quoted so it wont show up as a RIGHT_PAREN
    # token.
    if tokens[0].type is lexer.TokenType.RIGHT_PAREN:
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      active_depth.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      if (state_ > parsing_name and
          get_tag(tokens[0]) in ("unsort", "unsortable")):
        sortable = False
      child = TreeNode(NodeType.COMMENT)
      active_depth.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    if state_ is parsing_name:
      token = tokens.pop(0)
      parg_group = TreeNode(NodeType.PARGGROUP)
      active_depth = parg_group
      tree.children.append(parg_group)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_flags:
      if get_normalized_kwarg(tokens[0]) in (
          "WIN32", "MACOSX_BUNDLE", "EXCLUDE_FROM_ALL"):
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      else:
        state_ += 1
        src_group = TreeNode(NodeType.PARGGROUP, sortable=sortable)
        active_depth = src_group
        tree.children.append(src_group)
    elif state_ is parsing_sources:
      token = tokens.pop(0)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      src_group.children.append(child)

      if only_comments_and_whitespace_remain(tokens, breakstack):
        active_depth = tree

  return tree


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


def get_first_semantic_token(tokens):
  """
  Return the first token with semantic meaning
  """
  skip_tokens = (lexer.TokenType.WHITESPACE,
                 lexer.TokenType.NEWLINE,
                 lexer.TokenType.COMMENT,
                 lexer.TokenType.BRACKET_COMMENT)

  for token in tokens:
    if token.type in skip_tokens:
      continue
    return token
  return None


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
  if not descriminator in parsemap:
    logger.warning("Invalid install form \"%s\" at %s", descriminator,
                   tokens[0].location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  return parsemap[descriminator](tokens, breakstack)


def parse_file_read(tokens, breakstack):
  """
  ::

    file(READ <filename> <variable>
         [OFFSET <offset>] [LIMIT <max-in>] [HEX])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#read
  """

  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "OFFSET", PositionalParser(1),
          "LIMIT", PositionalParser(1),
      },
      flags=[
          "READ",
          "HEX"
      ],
      breakstack=breakstack)


def parse_file_strings(tokens, breakstack):
  """
  ::

    file(STRINGS <filename> <variable> [<options>...])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#read
  """

  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "LENGTH_MAXIMUM", PositionalParser(1),
          "LENGTH_MINIMUM", PositionalParser(1),
          "LIMIT_COUNT", PositionalParser(1),
          "LIMIT_INPUT", PositionalParser(1),
          "LIMIT_OUTPUT", PositionalParser(1),
          "REGEX", PositionalParser(1),
          "ENCODING", PositionalParser(1, flags=[
              "UTF-8", "UTF-16LE", "UTF-16BE", "UTF-32LE", "UTF-32BE"
          ]),
      },
      flags=[
          "STRINGS",
          "NEWLINE_CONSUME",
          "NO_HEX_CONVERSION",

      ],
      breakstack=breakstack)


HASH_STRINGS = [
    "MD5",
    "SHA1",
    "SHA224",
    "SHA256",
    "SHA384",
    "SHA512",
    "SHA3_224",
    "SHA3_256",
    "SHA3_384",
    "SHA3_512",
]


def parse_file_hash(tokens, breakstack):
  """
  ::

    file(<HASH> <filename> <variable>)

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#strings
  """

  return parse_standard(
      tokens,
      npargs=3,
      kwargs={},
      flags=HASH_STRINGS,
      breakstack=breakstack)


def parse_file_timestamp(tokens, breakstack):
  """
  ::

    file(TIMESTAMP <filename> <variable> [<format>] [UTC])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#strings
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={},
      flags=["TIMESTAMP", "UTC"],
      breakstack=breakstack)


def parse_file_write(tokens, breakstack):
  """
  ::

    file(WRITE <filename> <content>...)
    file(APPEND <filename> <content>...)

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#writing
  """
  tree = TreeNode(NodeType.ARGGROUP)
  consume_whitespace_and_comments(tokens, tree)
  tree.children.append(
      parse_positionals(tokens, 2, ["WRITE", "APPEND"], breakstack))
  consume_whitespace_and_comments(tokens, tree)
  tree.children.append(
      parse_positionals(tokens, '+', [], breakstack))

  return tree


def parse_file_generate_output(tokens, breakstack):
  """
  ::

    file(GENERATE OUTPUT output-file
        <INPUT input-file|CONTENT content>
        [CONDITION expression])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#writing
  """

  return parse_standard(
      tokens,
      npargs='1',
      kwargs={
          "OUTPUT": PositionalParser(1),
          "INPUT": PositionalParser(1),
          "CONTENT": PositionalParser('+'),
          "CONDITION": parse_conditional,
      },
      flags=["GENERATE"],
      breakstack=breakstack)


def parse_file_glob(tokens, breakstack):
  """
  ::

    file(GLOB <variable>
        [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS]
        [<globbing-expressions>...])
    file(GLOB_RECURSE <variable> [FOLLOW_SYMLINKS]
        [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS]
        [<globbing-expressions>...])
  :see: https://cmake.org/cmake/help/v3.14/command/file.html#filesystem
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={
          "LIST_DIRECTORIES": PositionalParser(1),
          "RELATIVE": PositionalParser(1)
      },
      flags=[
          "GLOB",
          "GLOB_RECURSE",
          "CONFIGURE_DEPENDS",
          "FOLLOW_SYMLINKS"],
      breakstack=breakstack)


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


def parse_file_copy(tokens, breakstack):
  """
  ::

    file(<COPY|INSTALL> <files>... DESTINATION <dir>
         [FILE_PERMISSIONS <permissions>...]
         [DIRECTORY_PERMISSIONS <permissions>...]
         [NO_SOURCE_PERMISSIONS] [USE_SOURCE_PERMISSIONS]
         [FILES_MATCHING]
         [[PATTERN <pattern> | REGEX <regex>]
          [EXCLUDE] [PERMISSIONS <permissions>...]] [...])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#filesystem
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={
          "DESTINATION": PositionalParser(1),
          "FILE_PERMISSIONS": PositionalParser('+'),
          "DIRECTORY_PERMISSIONS": PositionalParser('+'),
          "PATTERN": parse_pattern,
          "REGEX": parse_pattern,
      },
      flags=[
          "COPY",
          "INSTALL",
          "NO_SOURCE_PERMISSIONS",
          "USE_SOURCE_PERMISSIONS",
          "FILES_MATCHING",
      ],
      breakstack=breakstack)


def parse_file_create_link(tokens, breakstack):
  """
  ::

    file(CREATE_LINK <original> <linkname>
        [RESULT <result>] [COPY_ON_ERROR] [SYMBOLIC])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#filesystem
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={
          "RESULT": PositionalParser(1),
      },
      flags=[
          "COPY_ON_ERROR",
          "SYMBOLIC",
      ],
      breakstack=breakstack)


def parse_file_xfer(tokens, breakstack):
  """
  ::

    file(DOWNLOAD <url> <file> [<options>...])
    file(UPLOAD   <file> <url> [<options>...])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#transfer
  """

  return parse_standard(
      tokens,
      npargs='3',
      kwargs={
          "INACTIVITY_TIMEOUT": PositionalParser(1),
          "LOG": PositionalParser(1),
          "STATUS": PositionalParser(1),
          "TIMEOUT": PositionalParser(1),
          "USERPWD": PositionalParser(1),
          "HTTPHEADER": PositionalParser(1),
          "NETRC": PositionalParser(
              1, flags=["CMAKE_NETRC", "IGNORED", "OPTIONAL", "REQUIRED"]),
          "NETRC_FILE": PositionalParser(1),
          "EXPECTED_HASH": PositionalParser(1),
          "EXPECTED_MD5": PositionalParser(1),
          "TLS_VERIFY": PositionalParser(1),
          "TLS_CAINFO": PositionalParser(1),
      },
      flags=[
          "DOWNLOAD",
          "UPLOAD",
          "SHOW_PROGRESS",

      ],
      breakstack=breakstack)


def parse_file_lock(tokens, breakstack):
  """
  ::

    file(LOCK <path> [DIRECTORY] [RELEASE]
         [GUARD <FUNCTION|FILE|PROCESS>]
         [RESULT_VARIABLE <variable>]
         [TIMEOUT <seconds>])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html#locking
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={
          "GUARD": PositionalParser(1, flags=["FUNCTION", "FILE", "PROCESS"]),
          "RESULT_VARIABLE": PositionalParser(1),
          "TIMEOUT": PositionalParser(1)
      },
      flags=[
          "LOCK",
          "DIRECTORY",
          "RELEASE",
      ],
      breakstack=breakstack)


def parse_file(tokens, breakstack):
  """
  The ``file()`` command has a lot of different forms, depending on the first
  argument. This function just dispatches the correct parse implementation for
  the given form::

    Reading
      file(READ <filename> <out-var> [...])
      file(STRINGS <filename> <out-var> [...])
      file(<HASH> <filename> <out-var>)
      file(TIMESTAMP <filename> <out-var> [...])

    Writing
      file({WRITE | APPEND} <filename> <content>...)
      file({TOUCH | TOUCH_NOCREATE} [<file>...])
      file(GENERATE OUTPUT <output-file> [...])

    Filesystem
      file({GLOB | GLOB_RECURSE} <out-var> [...] [<globbing-expr>...])
      file(RENAME <oldname> <newname>)
      file({REMOVE | REMOVE_RECURSE } [<files>...])
      file(MAKE_DIRECTORY [<dir>...])
      file({COPY | INSTALL} <file>... DESTINATION <dir> [...])
      file(SIZE <filename> <out-var>)
      file(READ_SYMLINK <linkname> <out-var>)
      file(CREATE_LINK <original> <linkname> [...])

    Path Conversion
      file(RELATIVE_PATH <out-var> <directory> <file>)
      file({TO_CMAKE_PATH | TO_NATIVE_PATH} <path> <out-var>)

    Transfer
      file(DOWNLOAD <url> <file> [...])
      file(UPLOAD <file> <url> [...])

    Locking
      file(LOCK <path> [...])

  :see: https://cmake.org/cmake/help/v3.14/command/file.html
  """

  descriminator_token = get_first_semantic_token(tokens)
  if descriminator_token is None:
    logger.warning("Invalid empty file() command at %s",
                   tokens[0].get_location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  descriminator = descriminator_token.spelling.upper()
  parsemap = {
      "READ": parse_file_read,
      "STRINGS": parse_file_strings,
      "TIMESTAMP": parse_file_timestamp,
      "WRITE": parse_file_write,
      "APPEND": parse_file_write,
      "TOUCH": PositionalParser('+', ["TOUCH"]),
      "TOUCH_NO_CREATE": PositionalParser('+', ["TOUCH_NO_CREATE"]),
      "GLOB": parse_file_glob,
      "GLOB_RECURSE": parse_file_glob,
      "RENAME": PositionalParser(3, ["RENAME"]),
      "REMOVE": PositionalParser('+', ["REMOVE"]),
      "REMOVE_RECURSE": PositionalParser('+', ["REMOVE_RECURSE"]),
      "MAKE_DIRECTORY": PositionalParser('+', ["MAKE_DIRECTORY"]),
      "COPY": parse_file_copy,
      "INSTALL": parse_file_copy,
      "SIZE": PositionalParser(3, ["SIZE"]),
      "READ_SYMLINK": PositionalParser(3, ["READ_SYMLINK"]),
      "CREATE_LINK": parse_file_create_link,
      "RELATIVE_PATH": PositionalParser(4, ["RELATIVE_PATH"]),
      "TO_CMAKE_PATH": PositionalParser(3, ["TO_CMAKE_PATH"]),
      "TO_NATIVE_PATH": PositionalParser(3, ["TO_NATIVE_PATH"]),
      "DOWNLOAD": parse_file_xfer,
      "UPLOAD": parse_file_xfer,
      "LOCK": parse_file_lock
  }
  for hashname in HASH_STRINGS:
    parsemap[hashname] = parse_file_hash

  if not descriminator in parsemap:
    logger.warning("Invalid file() form \"%s\" at %s", descriminator,
                   tokens[0].location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  return parsemap[descriminator](tokens, breakstack)


def parse_external_project_add(tokens, breakstack):
  """
  ::

    ExternalProject_Add(<name> [<option>...])

  :see: https://cmake.org/cmake/help/v3.14/module/ExternalProject.html
  """
  return parse_standard(
      tokens,
      npargs=1,
      kwargs={
          # Directory Options
          "PREFIX": PositionalParser(1),
          "TMP_DIR": PositionalParser(1),
          "STAMP_DIR": PositionalParser(1),
          "LOG_DIR": PositionalParser(1),
          "DOWNLOAD_DIR": PositionalParser(1),
          "SOURCE_DIR": PositionalParser(1),
          "BINARY_DIR": PositionalParser(1),
          "INSTALL_DIR": PositionalParser(1),
          # Download Step Options
          "DOWNLOAD_COMMAND": parse_shell_command,
          "URL": PositionalParser('+'),
          "URL_HASH": PositionalParser(1),
          "URL_MD5": PositionalParser(1),
          "DOWNLOAD_NAME": PositionalParser(1),
          "DOWNLOAD_NO_EXTRACT": PositionalParser(1),
          "DOWNLOAD_NO_PROGRESS": PositionalParser(1),
          "TIMEOUT": PositionalParser(1),
          "HTTP_USERNAME": PositionalParser(1),
          "HTTP_PASSWORD": PositionalParser(1),
          "HTTP_HEADER": PositionalParser('+'),
          "TLS_VERIFY": PositionalParser(1),
          "TLS_CAINFO": PositionalParser(1),
          "NETRC": PositionalParser(
              1, flags=["CMAKE_NETRC", "IGNORED", "OPTIONAL", "REQUIRED"]),
          "NETRC_FILE": PositionalParser(1),
          # Git
          "GIT_REPOSITORY": PositionalParser(1),
          "GIT_TAG": PositionalParser(1),
          "GIT_REMOTE_NAME": PositionalParser(1),
          "GIT_SUBMODULES": PositionalParser('+'),
          "GIT_SHALLOW": PositionalParser(1),
          "GIT_PROGRESS": PositionalParser(1),
          "GIT_CONFIG": PositionalParser('+'),
          # Subversion
          "SVN_REPOSITORY": PositionalParser(1),
          "SVN_REVISION": PositionalParser(1),
          "SVN_USERNAME": PositionalParser(1),
          "SVN_PASSWORD": PositionalParser(1),
          "SVN_TRUST_CERT": PositionalParser(1),
          # Mercurial
          "HG_REPOSITORY": PositionalParser(1),
          "HG_TAG": PositionalParser(1),
          # CVS
          "CVS_REPOSITORY": PositionalParser(1),
          "CVS_MODULE": PositionalParser(1),
          "CVS_TAG": PositionalParser(1),
          # Update/Patch Step Options
          "UPDATE_COMMAND": parse_shell_command,
          "UPDATE_DISCONNECTED": PositionalParser(1),
          "PATCH_COMMAND": parse_shell_command,
          # Configure Step Options
          "CONFIGURE_COMMAND": parse_shell_command,
          "CMAKE_COMMAND": PositionalParser(1),
          "CMAKE_GENERATOR": PositionalParser(1),
          "CMAKE_GENERATOR_PLATFORM": PositionalParser(1),
          "CMAKE_GENERATOR_TOOLSET": PositionalParser(1),
          "CMAKE_GENERATOR_INSTANCE": PositionalParser(1),
          "CMAKE_ARGS": PositionalParser('+'),
          "CMAKE_CACHE_ARGS": PositionalParser('+'),
          "CMAKE_CACHE_DEFAULT_ARGS": PositionalParser('+'),
          "SOURCE_SUBDIR": PositionalParser(1),
          # Build Step Options
          "BUILD_COMMAND": parse_shell_command,
          "BUILD_IN_SOURCE": PositionalParser(1),
          "BUILD_ALWAYS": PositionalParser(1),
          "BUILD_BYPRODUCTS": PositionalParser('+'),
          # Install Step Options
          "INSTALL_COMMAND": parse_shell_command,
          # Test Step Options
          "TEST_COMMAND": parse_shell_command,
          "TEST_BEFORE_INSTALL": PositionalParser(1),
          "TEST_AFTER_INSTALL": PositionalParser(1),
          "TEST_EXCLUDE_FROM_MAIN": PositionalParser(1),
          # Output Logging Options
          "LOG_DOWNLOAD": PositionalParser(1),
          "LOG_UPDATE": PositionalParser(1),
          "LOG_PATCH": PositionalParser(1),
          "LOG_CONFIGURE": PositionalParser(1),
          "LOG_BUILD": PositionalParser(1),
          "LOG_INSTALL": PositionalParser(1),
          "LOG_TEST": PositionalParser(1),
          "LOG_MERGED_STDOUTERR": PositionalParser(1),
          "LOG_OUTPUT_ON_FAILURE": PositionalParser(1),
          # Terminal Access Options
          "USES_TERMINAL_DOWNLOAD": PositionalParser(1),
          "USES_TERMINAL_UPDATE": PositionalParser(1),
          "USES_TERMINAL_CONFIGURE": PositionalParser(1),
          "USES_TERMINAL_BUILD": PositionalParser(1),
          "USES_TERMINAL_INSTALL": PositionalParser(1),
          "USES_TERMINAL_TEST": PositionalParser(1),
          # Target Options
          "DEPENDS": PositionalParser('+'),
          "EXCLUDE_FROM_ALL": PositionalParser(1),
          "STEP_TARGETS": PositionalParser('+'),
          "INDEPENDENT_STEP_TARGETS": PositionalParser('+'),
          # Misc Options
          "LIST_SEPARATOR": PositionalParser(1),
          "COMMAND": parse_shell_command,
      },
      flags=[],
      breakstack=breakstack)


def parse_external_project_add_step(tokens, breakstack):
  """
  ::

    ExternalProject_Add_Step(<name> [<option>...])

  :see: https://cmake.org/cmake/help/v3.14/module/ExternalProject.html#command:externalproject_add_step
  """
  return parse_standard(
      tokens,
      npargs=2,
      kwargs={
          "COMMAND": parse_shell_command,
          "COMMENT": PositionalParser('+'),
          "DEPENDEES": PositionalParser('+'),
          "DEPENDERS": PositionalParser('+'),
          "DEPENDS": PositionalParser('+'),
          "BYPRODUCTS": PositionalParser('+'),
          "ALWAYS": PositionalParser(1),
          "EXCLUDE_FROM_MAIN": PositionalParser(1),
          "WORKING_DIRECTORY": PositionalParser(1),
          "LOG": PositionalParser(1),
          "USES_TERMINAL": PositionalParser(1),
      },
      flags=[],
      breakstack=breakstack)


def parse_fetchcontent_declare(tokens, breakstack):
  """
  ::

    FetchContent_Declare(<name> <contentOptions>...)

  :see: https://cmake.org/cmake/help/v3.14/module/FetchContent.html?highlight=fetchcontent#command:fetchcontent_declare
  """
  return parse_standard(
      tokens,
      npargs=1,
      kwargs={
          # Download Step Options
          "DOWNLOAD_COMMAND": parse_shell_command,
          "URL": PositionalParser('+'),
          "URL_HASH": PositionalParser(1),
          "URL_MD5": PositionalParser(1),
          "DOWNLOAD_NAME": PositionalParser(1),
          "DOWNLOAD_NO_EXTRACT": PositionalParser(1),
          "DOWNLOAD_NO_PROGRESS": PositionalParser(1),
          "TIMEOUT": PositionalParser(1),
          "HTTP_USERNAME": PositionalParser(1),
          "HTTP_PASSWORD": PositionalParser(1),
          "HTTP_HEADER": PositionalParser('+'),
          "TLS_VERIFY": PositionalParser(1),
          "TLS_CAINFO": PositionalParser(1),
          "NETRC": PositionalParser(
              1, flags=["CMAKE_NETRC", "IGNORED", "OPTIONAL", "REQUIRED"]),
          "NETRC_FILE": PositionalParser(1),
          # Git
          "GIT_REPOSITORY": PositionalParser(1),
          "GIT_TAG": PositionalParser(1),
          "GIT_REMOTE_NAME": PositionalParser(1),
          "GIT_SUBMODULES": PositionalParser('+'),
          "GIT_SHALLOW": PositionalParser(1),
          "GIT_PROGRESS": PositionalParser(1),
          "GIT_CONFIG": PositionalParser('+'),
          # Subversion
          "SVN_REPOSITORY": PositionalParser(1),
          "SVN_REVISION": PositionalParser(1),
          "SVN_USERNAME": PositionalParser(1),
          "SVN_PASSWORD": PositionalParser(1),
          "SVN_TRUST_CERT": PositionalParser(1),
          # Mercurial
          "HG_REPOSITORY": PositionalParser(1),
          "HG_TAG": PositionalParser(1),
          # CVS
          "CVS_REPOSITORY": PositionalParser(1),
          "CVS_MODULE": PositionalParser(1),
          "CVS_TAG": PositionalParser(1),
          # Update/Patch Step Options
          "UPDATE_COMMAND": parse_shell_command,
          "UPDATE_DISCONNECTED": PositionalParser(1),
          "PATCH_COMMAND": parse_shell_command,
      },
      flags=[],
      breakstack=breakstack)


def parse_fetchcontent_populate(tokens, breakstack):
  """
  ::

    FetchContent_Populate( <name>
      [QUIET]
      [SUBBUILD_DIR <subBuildDir>]
      [SOURCE_DIR <srcDir>]
      [BINARY_DIR <binDir>]
      ...
    )

  :see: https://cmake.org/cmake/help/v3.14/module/FetchContent.html?highlight=fetchcontent#command:fetchcontent_populate
  """
  return parse_standard(
      tokens,
      npargs=1,
      kwargs={
          "SUBBUILD_DIR": PositionalParser(1),
          "SOURCE_DIR": PositionalParser(1),
          "BINARY_DIR": PositionalParser(1),
          # Download Step Options
          "DOWNLOAD_COMMAND": parse_shell_command,
          "URL": PositionalParser('+'),
          "URL_HASH": PositionalParser(1),
          "URL_MD5": PositionalParser(1),
          "DOWNLOAD_NAME": PositionalParser(1),
          "DOWNLOAD_NO_EXTRACT": PositionalParser(1),
          "DOWNLOAD_NO_PROGRESS": PositionalParser(1),
          "TIMEOUT": PositionalParser(1),
          "HTTP_USERNAME": PositionalParser(1),
          "HTTP_PASSWORD": PositionalParser(1),
          "HTTP_HEADER": PositionalParser('+'),
          "TLS_VERIFY": PositionalParser(1),
          "TLS_CAINFO": PositionalParser(1),
          "NETRC": PositionalParser(
              1, flags=["CMAKE_NETRC", "IGNORED", "OPTIONAL", "REQUIRED"]),
          "NETRC_FILE": PositionalParser(1),
          # Git
          "GIT_REPOSITORY": PositionalParser(1),
          "GIT_TAG": PositionalParser(1),
          "GIT_REMOTE_NAME": PositionalParser(1),
          "GIT_SUBMODULES": PositionalParser('+'),
          "GIT_SHALLOW": PositionalParser(1),
          "GIT_PROGRESS": PositionalParser(1),
          "GIT_CONFIG": PositionalParser('+'),
          # Subversion
          "SVN_REPOSITORY": PositionalParser(1),
          "SVN_REVISION": PositionalParser(1),
          "SVN_USERNAME": PositionalParser(1),
          "SVN_PASSWORD": PositionalParser(1),
          "SVN_TRUST_CERT": PositionalParser(1),
          # Mercurial
          "HG_REPOSITORY": PositionalParser(1),
          "HG_TAG": PositionalParser(1),
          # CVS
          "CVS_REPOSITORY": PositionalParser(1),
          "CVS_MODULE": PositionalParser(1),
          "CVS_TAG": PositionalParser(1),
          # Update/Patch Step Options
          "UPDATE_COMMAND": parse_shell_command,
          "UPDATE_DISCONNECTED": PositionalParser(1),
          "PATCH_COMMAND": parse_shell_command,
      },
      flags=[
          "QUIET"
      ],
      breakstack=breakstack)


def parse_fetchcontent_getproperties(tokens, breakstack):
  """
  ::

    FetchContent_GetProperties( <name>
      [SOURCE_DIR <srcDirVar>]
      [BINARY_DIR <binDirVar>]
      [POPULATED <doneVar>]
    )
  """
  return parse_standard(
      tokens,
      npargs=1,
      kwargs={
          "SOURCE_DIR": PositionalParser(1),
          "BINARY_DIR": PositionalParser(1),
          "POPULATED": PositionalParser(1),
      },
      flags=[],
      breakstack=breakstack)


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


def parse_add_custom_command(tokens, breakstack):
  """
  ::

    add_custom_command(OUTPUT output1 [output2 ...]
                       COMMAND command1 [ARGS] [args1...]
                       [COMMAND command2 [ARGS] [args2...] ...]
                       [MAIN_DEPENDENCY depend]
                       [DEPENDS [depends...]]
                       [IMPLICIT_DEPENDS <lang1> depend1
                                        [<lang2> depend2] ...]
                       [WORKING_DIRECTORY dir]
                       [COMMENT comment] [VERBATIM] [APPEND])

  :see: https://cmake.org/cmake/help/v3.0/command/add_custom_command.html
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "COMMAND": parser.parse_shell_command,
          "COMMENT": parser.PositionalParser('*'),
          "DEPENDS": parser.PositionalParser('*'),
          "IMPLICIT_DEPENDS": parser.PositionalTupleParser('+', 2),
          "MAIN_DEPENDENCY": parser.PositionalParser(1),
          "OUTPUT": parser.PositionalParser('+'),
          "WORKING_DIRECTORY": parser.PositionalParser(1)
      },
      flags=["APPEND", "VERBATIM",
             "PRE_BUILD", "PRE_LINK", "POST_BUILD"],
      breakstack=breakstack)


def get_parse_db():
  """
  Returns a dictionary mapping statement name to parse functor for that
  statement.
  """

  parse_db = {}
  parse_db["add_custom_command"] = parse_add_custom_command
  parse_db["add_library"] = parse_add_library
  parse_db["add_executable"] = parse_add_executable
  parse_db["install"] = parse_install
  parse_db["file"] = parse_file

  # Standard, non-builtin commands
  parse_db["externalproject_add"] = parse_external_project_add
  parse_db["externalproject_get_property"] = StandardParser('+')
  parse_db["externalproject_add_step"] = parse_external_project_add_step
  parse_db["externalproject_add_steptargets"] = \
      PositionalParser('+', flags=["NO_DEPENDS"])
  parse_db["externalproject_add_stepdependencies"] = PositionalParser('+')
  parse_db["fetchcontent_declare"] = parse_fetchcontent_declare
  parse_db["fetchcontent_populate"] = parse_fetchcontent_populate
  parse_db["fetchcontent_getproperties"] = parse_fetchcontent_getproperties
  parse_db["fetchcontent_makeavailable"] = PositionalParser('+')
  parse_db["set"] = parse_set

  for key in ("if", "elseif", "while"):
    parse_db[key] = parser.parse_conditional

  return parse_db
