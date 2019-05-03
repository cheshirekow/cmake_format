import logging

from cmake_format.parser import (
    get_first_semantic_token,
    parse_pattern,
    parse_standard,
    PositionalParser,
)

logger = logging.getLogger("cmake-format")


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


def populate_db(parse_db):
  parse_db["install"] = parse_install
