import logging

from cmake_format.parser import (
    parse_standard,
    parse_shell_command,
    PositionalParser,
    PositionalTupleParser,
)

logger = logging.getLogger("cmake-format")


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
          "COMMAND": parse_shell_command,
          "COMMENT": PositionalParser('*'),
          "DEPENDS": PositionalParser('*'),
          "IMPLICIT_DEPENDS": PositionalTupleParser('+', 2),
          "MAIN_DEPENDENCY": PositionalParser(1),
          "OUTPUT": PositionalParser('+'),
          "WORKING_DIRECTORY": PositionalParser(1)
      },
      flags=["APPEND", "VERBATIM",
             "PRE_BUILD", "PRE_LINK", "POST_BUILD"],
      breakstack=breakstack)


def populate_db(parse_db):
  parse_db["add_custom_command"] = parse_add_custom_command
