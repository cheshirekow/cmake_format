# test: descriminator_hidden_behind_variable
set(libtype OBJECT)
add_library(foobar ${libtype} ${alpha}.cc bar.cc baz.cc foo.cc)

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
add_library(foobar foo.cc)

# test: all_arguments
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
add_library(
  foobar STATIC EXCLUDE_FROM_ALL
  sourcefile_01.cc
  sourcefile_02.cc
  sourcefile_03.cc
  sourcefile_04.cc
  sourcefile_05.cc
  sourcefile_06.cc
  sourcefile_07.cc)

# test: parse_with_trailing_argcomment
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
          (NodeType.ARGUMENT, [
            (NodeType.COMMENT, []),
          ]),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_library(
  foo STATIC EXCLUDE_FROM_ALL foo.cc bar.cc # This is a concluding comment
)

# test: disable_autosort_with_tag
#[=[
autosort = True
]=]
add_library(foobar STATIC # cmake-format: unsort
            sourcefile_04.cc sourcefile_03.cc sourcefile_01.cc sourcefile_02.cc)

# test: imported_form
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
          (NodeType.FLAG, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_library(foobar SHARED IMPORTED GLOBAL)

# test: object_form
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
        ]),
        (NodeType.PARGGROUP, [
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
add_library(foobar OBJECT bar.cc baz.cc foo.cc)

# test: alias_form
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
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_library(foobar ALIAS foobarbaz)

# test: interface_form
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
          (NodeType.FLAG, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
add_library(foobar INTERFACE IMPORTED GLOBAL)
