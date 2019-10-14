# cmftest-begin: test_nonargument_terminal_comments
add_library(
  foo
  # This comment is not attached to an argument
  bar.cc foo.cc)

find_package(
  foobar REQUIRED
  COMPONENTS some_component # some_other_component
             # This is a very long comment, and actually the second comment in
             # this row.
)
# cmftest-end

# cmftest-begin: test_arg_just_fits_two
message(
  FATAL_ERROR "81 character line ----------------------------------------")
# cmftest-end
