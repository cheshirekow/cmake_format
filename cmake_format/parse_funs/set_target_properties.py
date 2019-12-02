from cmake_format.parser import PositionalTupleParser, parse_standard


def parse_set_target_properties(tokens, breakstack):
  """
  ::
    set_target_properties(target1 target2 ...
                        PROPERTIES prop1 value1
                        prop2 value2 ...)
  """

  return parse_standard(
      tokens,
      npargs='+',
      kwargs={
          "PROPERTIES": PositionalTupleParser(2, '+', [])
      },
      flags=[],
      breakstack=breakstack)


def populate_db(parse_db):
  parse_db["set_target_properties"] = parse_set_target_properties
