# test: discriminator_hidden_behind_variable
# Ensure that argument's aren't sorted in the event that we can't infer the form
# of the command.
set(exetype ALIAS)
set(alias foobarbaz)
add_executable(foobar ${exetype} ${alias})

# test: single_argument
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_executable(foobar foo.cc)

# test: all_arguments
#[=[
expect_parse =  [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
          (NodeType.FLAG, []),
          (NodeType.FLAG, []),
        ]),
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_executable(
  foobar WIN32 EXCLUDE_FROM_ALL
  sourcefile_01.cc
  sourcefile_02.cc
  sourcefile_03.cc
  sourcefile_04.cc
  sourcefile_05.cc
  sourcefile_06.cc
  sourcefile_07.cc)

# test: disable_autosort_with_tag
#[=[
autosort = True
]=]
add_executable(
  foobar WIN32 # cmake-format: unsort
  sourcefile_04.cc sourcefile_03.cc sourcefile_01.cc sourcefile_02.cc)

# test: imported_form
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
          (NodeType.FLAG, []),
          (NodeType.FLAG, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_executable(foobar IMPORTED GLOBAL)

# test: alias_form
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
          (NodeType.FLAG, []),
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_executable(foobar ALIAS foobarbaz)