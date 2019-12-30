# test: single_argument_a
#[=[
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

# test: standard_form
add_custom_command(
  OUTPUT output1 output2
  COMMAND command1 ARGS args1 args2 args3
  COMMAND command2 ARGS args1 args2 args3
  MAIN_DEPENDENCY depend
  DEPENDS depends1 depends2 depends3
  BYPRODUCTS files files files
  IMPLICIT_DEPENDS CXX depend1 CXX depend2
  WORKING_DIRECTORY dir
  COMMENT comment1
  DEPFILE depfile1
  JOB_POOL job_pool1
  VERBATIM APPEND USES_TERMINAL COMMAND_EXPAND_LISTS)

# test: event_form
add_custom_command(
  TARGET target1
  PRE_BUILD
  COMMAND command1 ARGS args1 args2 args3
  COMMAND command2 ARGS args1 args2 args3
  BYPRODUCTS files files files
  WORKING_DIRECTORY dir
  COMMENT comment1
  VERBATIM APPEND USES_TERMINAL COMMAND_EXPAND_LISTS)

# test: add_custom_target
add_custom_target(
  target1 ALL
  command1 args1 args2 args3
  COMMAND command2 args1 args2 args3
  DEPENDS depend1 depend2 depend3
  BYPRODUCTS file1 file2 file3
  WORKING_DIRECTORY dir
  COMMENT comment1
  JOB_POOL job_pool1
  VERBATIM USES_TERMINAL COMMAND_EXPAND_LISTS
  SOURCES src1 src2 src3 src4)
