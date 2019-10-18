# test: file_read
file(READ foobar.baz foobar_content)

# test: file_strings
file(STRINGS foobar.baz foorbar_content REGEX hello)

# test: file_hash
file(SHA1 foobar.baz foobar_digest)

# test: file_timestamp
file(TIMESTAMP foobar.baz foobar_timestamp)

# test: file_write
file(WRITE foobar.baz
     "first line of the output file long enough to force a wrap"
     "second line of the output file long enough to force a wrap")

# test: file_write_2
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.FLAG, []),
          (NodeType.ARGUMENT, []),
        ]),
        (NodeType.PARGGROUP, [
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
file(WRITE ${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
     "include(CMakeFindDependencyMacro)\n"
     "include(\${X}/${CMAKE_PROJECT_NAME}Targets.cmake)\n")

# test: file_append
file(APPEND foobar.baz
     "first line of the output file long enough to force a wrap"
     "second line of the output file long enough to force a wrap")

# test: file_generate_output
# TODO(josh): "file content line three" should probably be on the next line
file(
  GENERATE
  OUTPUT foobar.baz
  CONTENT "file content line one" #
          "file content line two" "file content line three"
  CONDITION (FOO AND BAR) OR BAZ)

# test: file_glob
file(
  GLOB globout
  RELATIVE foo/bar/baz
  "*.py" "*.txt")

# test: file_copy
file(
  COPY foo bar baz
  DESTINATION foobar
  FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
  FILES_MATCHING
  PATTERN "*.h"
  REGEX ".*\\.cc")
