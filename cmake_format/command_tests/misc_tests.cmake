# test: nonargument_terminal_comments
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

# test: arg_just_fits_two
message(
  FATAL_ERROR "81 character line ----------------------------------------")

# test: comment_before_command
# This comment should remain right before the command call. Furthermore, the
# command call should be formatted to a single line.
add_subdirectories(foo bar baz foo2 bar2 baz2)

# test: paragraphs_preserved
# This is a paragraph
#
# This is a second paragraph
#
# This is a third paragraph

# test: complex_nested_stuff
if(foo)
  if(sbar)
    # This comment is in-scope.
    add_library(
      foo_bar_baz
      foo.cc bar.cc # this is a comment for arg2 this is more comment for arg2,
                    # it should be joined with the first.
      baz.cc) # This comment is part of add_library

    other_command(
      some_long_argument some_long_argument) # this comment is very long and
                                             # gets split across some lines

    other_command(
      some_long_argument some_long_argument some_long_argument) # this comment
                                                                # is even longer
                                                                # and wouldn't
                                                                # make sense to
                                                                # pack at the
                                                                # end of the
                                                                # command so it
                                                                # gets it's own
                                                                # lines
  endif()
endif()

# test: custom_command
# This very long command should be broken up along keyword arguments
foo(nonkwarg_a nonkwarg_b
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo
    bar baz)

# test: multiline_string
foo(some_arg some_arg "
    This string is on multiple lines
")

# test: format_off_code
# No, I really want this to look ugly
# cmake-format: off
add_library(a b.cc
  c.cc         d.cc
          e.cc)
# cmake-format: on

# test: multiline_statment_comment_idempotent
set(HELLO hello world!) # TODO(josh): fix this bad code with some change that
                        # takes mutiple lines to explain

# test: function_def
function(forbarbaz arg1)
  do_something(arg1 ${ARGN})
endfunction()

# test: macro_def
macro(forbarbaz arg1)
  do_something(arg1 ${ARGN})
endmacro()

# test: comment_fences
# ~~~
#   This is some
#  verbatim text
#      that should not be
# formatted
# ~~~

# test: bracket_comments
#[[This is a bracket comment.
It is preserved verbatim, but trailing whitespace is removed.
So things like --this-- Are fine:]]

# test: bracket_comment_nested
if(foo)
  #[==[This is a bracket comment at some nested level
       it is preserved verbatim, but trailing
       whitespace is removed.]==]
endif()

# test: bracket_comment_inline
message("First Argument" #[[Bracket Comment]] "Second Argument")

# test: comment_after_command
foo_command() # comment

# test: comment_in_statment
add_library(foo # This comment is not attached to an argument
            bar.cc foo.cc)

# test: comment_at_end_of_statement_a
add_library(foo bar.cc foo.cc # This comment is not attached to an argument
)

# test: comment_at_end_of_statement_b
target_link_libraries(
  libraryname PUBLIC ${COMMON_LIBRARIES} # add more library dependencies here
)

# test: comment_at_end_of_statment_c
find_package(
  foobar REQUIRED
  COMPONENTS some_component # some_other_component
             # This is a very long comment, and actually the second comment in
             # this row.
)

# test: elseif
if(MSVC)

elseif(
  (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
  OR CMAKE_COMPILER_IS_GNUCC
  OR CMAKE_COMPILER_IS_GNUCXX)

endif()

# test: kwarg_match_consumes
add_test(NAME myTestName COMMAND testCommand --run_test=@quick)

# test: quoted_assignment_literal
target_compile_definitions(foo PUBLIC BAR="Quoted String"
                                      BAZ_______________________Z)

# test: canonical_spelling
ExternalProject_Add(
  foobar
  URL https://foobar.baz/latest.tar.gz
  TLS_VERIFY TRUE
  CONFIGURE_COMMAND configure
  BUILD_COMMAND make
  INSTALL_COMMAND make install)

# test: argcomment_preserved_and_reflowed
set(HEADERS
    header_a.h header_b.h # This comment should be preserved, moreover it should
                          # be split across two lines.
    header_c.h header_d.h)

# test: some_string_stuff
# This command uses a string with escaped quote chars
foo(some_arg some_arg "This is a \"string\" within a string")

# This command uses an empty string
foo(some_arg some_arg "")

# This command uses a multiline string
foo(some_arg some_arg "
    This string is on multiple lines
")

# test: foreach
foreach(forbarbaz arg1 arg2 arg3)
  message(hello ${foobarbaz})
endforeach()

# test: while
while(forbarbaz arg1 arg2 arg3)
  message(hello ${foobarbaz})
endwhile()

# test: ctrl_space
#[=[
separate_ctrl_name_with_space = True
]=]
if (foo)
  myfun(foo bar baz)
endif ()

# test: fn_space
#[=[
separate_fn_name_with_space = True
]=]
myfun (foo bar baz)

# test: nested_bullets
# This is a bulleted list:
#
# * item 1
# * item 2
#
#   * item 3
#   * item 4
#
#     * item 5
#     * item 6
#
# * item 7
# * item 8

# test: disable_markup
#[=[
enable_markup = False
]=]
# don't reflow
# or parse markup
# for these lines

# test: shebang_preserved
#!/usr/bin/cmake -P
