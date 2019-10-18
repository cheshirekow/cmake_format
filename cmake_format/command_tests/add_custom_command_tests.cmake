# test: single_argument_a
#[=[
max_subargs_per_line = 100
expect_parse = [
(NodeType.BODY, [
  (NodeType.STATEMENT, [
    (NodeType.FUNNAME, []),
    (NodeType.LPAREN, []),
    (NodeType.ARGGROUP, [
      (NodeType.KWARGGROUP, [
        (NodeType.KEYWORD, []),
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.KWARGGROUP, [
        (NodeType.KEYWORD, []),
        (NodeType.ARGGROUP, [
          (NodeType.PARGGROUP, [
            (NodeType.ARGUMENT, []),
            (NodeType.ARGUMENT, []),
            (NodeType.ARGUMENT, []),
            (NodeType.ARGUMENT, []),
            (NodeType.ARGUMENT, []),
          ]),
        ]),
      ]),
      (NodeType.KWARGGROUP, [
        (NodeType.KEYWORD, []),
        (NodeType.ARGGROUP, [
          (NodeType.PARGGROUP, [
            (NodeType.ARGUMENT, []),
            (NodeType.ARGUMENT, []),
          ]),
        ]),
      ]),
      (NodeType.KWARGGROUP, [
        (NodeType.KEYWORD, []),
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.KWARGGROUP, [
        (NodeType.KEYWORD, []),
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
      ]),
    ]),
    (NodeType.RPAREN, []),
  ]),
  (NodeType.WHITESPACE, []),
]),
]
]=]
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
  COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
          ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
  DEPENDS ${foobar_docs}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})