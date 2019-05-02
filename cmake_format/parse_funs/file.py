import logging

from cmake_format.parser import (
    consume_whitespace_and_comments,
    get_first_semantic_token,
    NodeType,
    parse_conditional,
    parse_pattern,
    parse_positionals,
    parse_standard,
    PositionalParser,
    TreeNode,
)

logger = logging.getLogger("cmake-format")


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
          "OFFSET": PositionalParser(1),
          "LIMIT": PositionalParser(1),
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
          "LENGTH_MAXIMUM": PositionalParser(1),
          "LENGTH_MINIMUM": PositionalParser(1),
          "LIMIT_COUNT": PositionalParser(1),
          "LIMIT_INPUT": PositionalParser(1),
          "LIMIT_OUTPUT": PositionalParser(1),
          "REGEX": PositionalParser(1),
          "ENCODING": PositionalParser(1, flags=[
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
      npargs=1,
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
      npargs='*',
      kwargs={
          "COPY": PositionalParser('*'),
          "DESTINATION": PositionalParser(1),
          "FILE_PERMISSIONS":
              PositionalParser(
                  '+',
                  flags=["OWNER_READ", "OWNER_WRITE", "OWNER_EXECUTE",
                         "GROUP_READ", "GROUP_WRITE", "GROUP_EXECUTE",
                         "WORLD_READ", "WORLD_WRITE", "WORLD_EXECUTE",
                         "SETUID", "SETGID"]),
          "DIRECTORY_PERMISSIONS": PositionalParser('+'),
          "PATTERN": parse_pattern,
          "REGEX": parse_pattern,
      },
      flags=[
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
      npargs=3,
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
      "GENERATE": parse_file_generate_output,
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

  if descriminator not in parsemap:
    logger.warning("Invalid file() form \"%s\" at %s", descriminator,
                   tokens[0].location())
    return parse_standard(tokens, npargs='*', kwargs={}, flags=[],
                          breakstack=breakstack)

  return parsemap[descriminator](tokens, breakstack)


def populate_db(parse_db):
  parse_db["file"] = parse_file
