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

# test: collapse_additional_newlines
#[==[
# The following multiple newlines should be collapsed into a single newline




cmake_minimum_required(VERSION 2.8.11)
project(cmakelang_test)
]==]
# The following multiple newlines should be collapsed into a single newline

cmake_minimum_required(VERSION 2.8.11)
project(cmakelang_test)

# test: multiline_reflow
#[==[
# This multiline-comment should be reflowed
# into a single comment
# on one line
]==]
# This multiline-comment should be reflowed into a single comment on one line

# test: long_args_command_split
#[==[
# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)
]==]
# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h
            very_long_header_name_c.h)

# test: lots_of_args_command_split
#[==[
# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc source_g.cc)
]==]
# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc
            source_g.cc)

# test: string_preserved_during_split
#[==[
# The string in this command should not be split
set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")
]==]
# The string in this command should not be split
set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS
                                             "-std=c++11 -Wall -Wextra")

# test: long_arg_on_newline
#[==[
# This command has a very long argument and can't be aligned with the command
# end, so it should be moved to a new line with block indent + 1.
some_long_command_name("Some very long argument that really needs to be on the next line.")
]==]
# This command has a very long argument and can't be aligned with the command
# end, so it should be moved to a new line with block indent + 1.
some_long_command_name(
  "Some very long argument that really needs to be on the next line.")

# test: long_kwargarg_on_newline
#[==[
# This situation is similar but the argument to a KWARG needs to be on a
# newline instead.
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
]==]
# This situation is similar but the argument to a KWARG needs to be on a newline
# instead.
set(CMAKE_CXX_FLAGS
    "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")

# test: argcomments_force_reflow
#[==[
cmake_parse_arguments(ARG
                "SILENT" # optional keywords
                "" # one value keywords
                "" # multi value keywords
                ${ARGN})
]==]
cmake_parse_arguments(
  ARG
  "SILENT" # optional keywords
  "" # one value keywords
  "" # multi value keywords
  ${ARGN})

# test: format_off
#[==[
# This part of the comment should
# be formatted
# but...
# cmake-format: off
# This bunny should remain untouched:
# . 　 ＿　∩
# 　　ﾚﾍヽ| |
# 　　　 (・ｘ・)
# 　　 c( uu}
# cmake-format: on
#          while this part should
#          be formatted again
]==]
# This part of the comment should be formatted but...
# cmake-format: off
# This bunny should remain untouched:
# . 　 ＿　∩
# 　　ﾚﾍヽ| |
# 　　　 (・ｘ・)
# 　　 c( uu}
# cmake-format: on
# while this part should be formatted again

# test: todo_preserved
#[==[
# This is a comment
# that should be joined but
# TODO(josh): This todo should not be joined with the previous line.
# NOTE(josh): Also this should not be joined with the todo.
]==]
# This is a comment that should be joined but
# TODO(josh): This todo should not be joined with the previous line.
# NOTE(josh): Also this should not be joined with the todo.

# test: always_dangle_first_parg_01
#[=[
always_dangle_first_parg = ['target_link_libraries']
]=]
#[==[
target_link_libraries(nonkwarg_a PUBLIC liba libb libc PRIVATE libd libe libf)
]==]
target_link_libraries(nonkwarg_a
  PUBLIC liba libb libc
  PRIVATE libd libe libf)

# test: always_wrap_01
#[=[
max_subgroups_hwrap = 100
always_wrap = ['foo']
]=]
#[==[
foo(nonkwarg_a HEADERS a.h SOURCES a.cc DEPENDS foo)
]==]
foo(nonkwarg_a
    HEADERS a.h
    SOURCES a.cc
    DEPENDS foo)

# test: always_wrap_02
#[=[
always_wrap = ['foo/HEADERS/PargGroupNode[0]']
]=]
#[==[
foo(nonkwarg_a HEADERS a.h b.h c.h SOURCES a.cc DEPENDS foo)
]==]
foo(nonkwarg_a
    HEADERS a.h
            b.h
            c.h
    SOURCES a.cc
    DEPENDS foo)

# test: preserve_separator_01
#[==[
# --------------------
# This is some
# text that I expect
# to reflow
# --------------------
]==]
# --------------------
# This is some text that I expect to reflow
# --------------------

# test: preserve_separator_02
#[==[
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
# This is some
# text that I expect
# to reflow
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
]==]
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
# This is some text that I expect to reflow
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*

# test: preserve_separator_03
#[==[
# ----Not Supported----
# This is some
# text that I expect
# to reflow
# ----Not Supported----
]==]
# ----Not Supported----
# This is some text that I expect to reflow
# ----Not Supported----

# test: bullets
#[==[
# This is a bulleted list:
#
#   * item 1
#   * item 2
# this line gets merged with item 2
#   * item 3 is really long and needs to be wrapped to a second line because it wont all fit on one line without wrapping.
#
# But the list has ended and this line is free. And
#   * this is not a bulleted list
#   * and it will be
#   * merged
]==]
# This is a bulleted list:
#
# * item 1
# * item 2 this line gets merged with item 2
# * item 3 is really long and needs to be wrapped to a second line because it
#   wont all fit on one line without wrapping.
#
# But the list has ended and this line is free. And * this is not a bulleted
# list * and it will be * merged

# test: enum_lists
#[==[
# This is a bulleted list:
#
#   1. item
#   2. item
#   3. item
#
#       4. item
#       5. item
#       6. item
#
#   1. item
#   3. item
#   5. item
#   6. item
#   6. item is really long and needs to be wrapped to a second line because it wont all fit on one line without wrapping.
#   7. item
#   9. item
#   9. item
#   9. item
#   9. item
#   9. item
#
]==]
# This is a bulleted list:
#
# 1. item
# 2. item
# 3. item
#
#   1. item
#   2. item
#   3. item
#
#  1. item
#  2. item
#  3. item
#  4. item
#  5. item is really long and needs to be wrapped to a second line because it wont
#     all fit on one line without wrapping.
#  6. item
#  7. item
#  8. item
#  9. item
# 10. item
# 11. item
#

# test: long_comment_after_command
#[==[
foo_command() # this is a long comment that exceeds the desired page width and will be wrapped to a newline
]==]
foo_command() # this is a long comment that exceeds the desired page width and
              # will be wrapped to a newline

# test: arg_just_fits_01
#[==[
message(FATAL_ERROR "81 character line ----------------------------------------")
]==]
message(
  FATAL_ERROR "81 character line ----------------------------------------")

# test: arg_just_fits_02
#[==[
message(FATAL_ERROR
        "100 character line ----------------------------------------------------------"
) # Closing parenthesis is indented one space!
]==]
message(
  FATAL_ERROR
    "100 character line ----------------------------------------------------------"
) # Closing parenthesis is indented one space!

# test: arg_just_fits_03
#[==[
message(
  "100 character line ----------------------------------------------------------------------"
) # Closing parenthesis is indented one space!
]==]
message(
  "100 character line ----------------------------------------------------------------------"
) # Closing parenthesis is indented one space!

# test: dangle_parens_01
#[=[
dangle_parens = True
]=]
foo_command()
foo_command(arg1)
foo_command(arg1) # comment

# test: dangle_parens_02
#[=[
dangle_parens = True
]=]
#[==[
some_long_command_name(longargname longargname longargname longargname longargname)
]==]
some_long_command_name(
  longargname longargname longargname longargname longargname
)

# test: dangle_parens_03
#[=[
dangle_parens = True
]=]
#[==[
if(foo)
  some_long_command_name(longargname longargname longargname longargname longargname)
endif()
]==]
if(foo)
  some_long_command_name(
    longargname longargname longargname longargname longargname
  )
endif()

# test: dangle_parens_04
#[=[
dangle_parens = True
]=]
#[==[
some_long_command_name(longargname longargname longargname longargname longargname longargname longargname longargname)
]==]
some_long_command_name(
  longargname
  longargname
  longargname
  longargname
  longargname
  longargname
  longargname
  longargname
)

# test: dangle_parens_05
#[=[
dangle_parens = True
]=]
#[==[

target_include_directories(target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)
]==]
target_include_directories(
  target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
)

# test: keyword_case_upper
#[=[
keyword_case = "upper"
]=]
#[==[
foo(bar baz)
]==]
foo(BAR BAZ)

# test: keyword_case_lower
#[=[
keyword_case = "lower"
]=]
#[==[
foo(BAR BAZ)
]==]
foo(bar baz)

# test: keyword_case_unchanged
#[=[
keyword_case = "unchanged"
]=]
#[==[
foo(BaR bAz)
]==]
foo(BaR bAz)

# test: command_case_lower
#[=[
command_case = "lower"
]=]
#[==[
FOO(bar baz)
]==]
foo(bar baz)

# test: command_case_upper
#[=[
command_case = "upper"
]=]
#[==[
foo(bar baz)
]==]
FOO(bar baz)

# test: command_case_unchnaged
#[=[
command_case = "unchanged"
]=]
#[==[
FoO(bar baz)
]==]
FoO(bar baz)

# test: comment_in_kwarg
#[==[
install(TARGETS foob
        ARCHIVE DESTINATION foobar
        # this is a line comment, not a comment on foobar
        COMPONENT baz)
]==]
install(
  TARGETS foob
  ARCHIVE DESTINATION foobar # this is a line comment, not a comment on foobar
          COMPONENT baz)

# test: elseif_else_control_space
#[=[
separate_ctrl_name_with_space = True
]=]
#[==[
if(foo)
elseif(bar)
else()
endif()
]==]
if (foo)

elseif (bar)

else ()

endif ()


# test: literal_first_comment_false
#[==[
# This comment
# is reflowed

# This comment
# is reflowed
]==]
# This comment is reflowed

# This comment is reflowed

# test: literal_first_comment_true
#[=[
first_comment_is_literal = True
]=]
#[==[
# This comment
# is not reflowed

# This comment
# is reflowed
]==]
# This comment
# is not reflowed

# This comment is reflowed

# test: preserve_copyright_false
#[==[
# Copyright 2018: Josh Bialkowski
# This text should not be reflowed
# because it's a copyright
]==]
# Copyright 2018: Josh Bialkowski This text should not be reflowed because it's
# a copyright


# test: preserve_copyright_true
#[=[
literal_comment_pattern = " Copyright.*"
]=]
# Copyright 2018: Josh Bialkowski
# This text should not be reflowed
# because it's a copyright

# test: percommand_override_base
#[==[
FoO(bar baz)
]==]
foo(bar baz)

# test: percommand_override_true
#[=[
per_command = {
  "foo": {
    "command_case": "unchanged"
  }
}
]=]
#[==[
FoO(bar baz)
]==]
FoO(bar baz)

# test: keyword_comment
#[==[
find_package(package REQUIRED
             COMPONENTS # --------------------------------------
                        # @TODO: This has to be filled manually
                        # --------------------------------------
                        this_is_a_really_long_word_foo)
]==]
find_package(
  package REQUIRED
  COMPONENTS # --------------------------------------
             # @TODO: This has to be filled manually
             # --------------------------------------
             this_is_a_really_long_word_foo)

# test: one_char_short_hpack_rparen_case
#[=[
# This was a particularly rare edge case. The situation is that the
# the arguments are one character shy of fitting in the configured line
# width, the statement column is the same as the indent column, and
# all the arguments are positional. The problem was that the hpack if
# possible logic did not account for the final paren. A fix is in place.
line_width = 132
tab_size = 4
]=]
#[==[
set(cubepp_HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
    ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)
]==]
set(cubepp_HDRS ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
                ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)

# test: layout_passes
#[=[
layout_passes = {
  "StatementNode": [(0, True)],
  "ArgGroupNode": [(0, True)],
  "PargGroupNode": [(0, True)],
}
]=]
add_library(
  foobar
  STATIC
  sourcefile_01.cc
  sourcefile_02.cc)

# test: trailing_comments
#[==[
set(foo bar

#< trailing comment
    #< more trailing comment
)
]==]
set(foo bar #< trailing comment more trailing comment
)

# test: trailing_comment_pattern
#[=[
explicit_trailing_pattern = "#<<"
]=]
#[==[
set(foo bar

#<< trailing comment
    #<< more trailing comment
)
]==]
set(foo bar #<< trailing comment more trailing comment
)

# test: rulers_preserved_without_markup
#[=[
enable_markup = False
]=]
#########################################################################
# Custom targets
#########################################################################

# test: comment_hashrulers_01
#[==[
##################
# This comment has a long block before it.
#############
]==]
# ##############################################################################
# This comment has a long block before it.
# ##############################################################################


# test: comment_hashrulers_02
#[==[
###############################################
# This is a section in the CMakeLists.txt file.
############
# This stuff below here
#     should get re-flowed like
# normal comments.  Across multiple
# lines and
#             beyond.
]==]
# ##############################################################################
# This is a section in the CMakeLists.txt file.
# ##############################################################################
# This stuff below here should get re-flowed like normal comments.  Across
# multiple lines and beyond.

# test: comment_hashrulers_03
#[=[
hashruler_min_length = 1000
]=]
#[==[
##########################################################################
# This comment has a long block before it.
##########################################################################
]==]
#
# This comment has a long block before it.
#

# test: comment_hashrulers_04
#[=[
hashruler_min_length = 1000
]=]
#[==[
##########################################################################
# This is a section in the CMakeLists.txt file.
##########################################################################
# This stuff below here
#     should get re-flowed like
# normal comments.  Across multiple
# lines and
#             beyond.
]==]
#
# This is a section in the CMakeLists.txt file.
#
# This stuff below here should get re-flowed like normal comments.  Across
# multiple lines and beyond.

# test: atword_statement
@PACKAGE_INIT@


# test: atword_with_comments
@PACKAGE_INIT@ # This is a trailing comment that requires multiple lines and
               # therefore should reflow.


# test: atword_with_comment_requires_wrap
#[==[
@PACKAGE_INIT@ # This-is-a-trailing-comment-that-requires-multiple-lines-and-therefore
               # should reflow.
]==]
@PACKAGE_INIT@
# This-is-a-trailing-comment-that-requires-multiple-lines-and-therefore should
# reflow.

# test: use_tabs
#[=[
use_tabchars = True
]=]
if(TRUE)
	message("Hello world")
endif()
