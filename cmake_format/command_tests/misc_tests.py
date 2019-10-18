# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
# pylint: disable=too-many-lines
from __future__ import unicode_literals

import io
import os
import unittest

from cmake_format import configuration
from cmake_format.command_tests import assert_format, TestBase


class TestMiscFormatting(TestBase):
  """
  Ensure that various inputs format the way we want them to
  """
  kExpectNumSidecarTests = 33

  def test_collapse_additional_newlines(self):
    self.source_str = """\
# The following multiple newlines should be collapsed into a single newline




cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

    self.expect_format = """\
# The following multiple newlines should be collapsed into a single newline

cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

  def test_multiline_reflow(self):
    self.source_str = """\
# This multiline-comment should be reflowed
# into a single comment
# on one line
"""
    self.expect_format = """\
# This multiline-comment should be reflowed into a single comment on one line
"""

  def test_long_args_command_split(self):
    self.source_str = """\
# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)
"""
    self.expect_format = """\
# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h
            very_long_header_name_c.h)
"""

  def test_lots_of_args_command_split(self):
    self.source_str = """\
# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc source_g.cc)
"""
    self.expect_format = """\
# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc
            source_g.cc)
"""

  def test_string_preserved_during_split(self):
    self.source_str = """\
# The string in this command should not be split
set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")
"""
    self.expect_format = """\
# The string in this command should not be split
set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS
                                             "-std=c++11 -Wall -Wextra")
"""

  def test_long_arg_on_newline(self):
    self.source_str = """\
# This command has a very long argument and can't be aligned with the command
# end, so it should be moved to a new line with block indent + 1.
some_long_command_name("Some very long argument that really needs to be on the next line.")
"""
    self.expect_format = """\
# This command has a very long argument and can't be aligned with the command
# end, so it should be moved to a new line with block indent + 1.
some_long_command_name(
  "Some very long argument that really needs to be on the next line.")
"""

  def test_long_kwargarg_on_newline(self):
    self.source_str = """\
# This situation is similar but the argument to a KWARG needs to be on a
# newline instead.
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
"""
    self.expect_format = """\
# This situation is similar but the argument to a KWARG needs to be on a newline
# instead.
set(CMAKE_CXX_FLAGS
    "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
"""

  def test_argcomments_force_reflow(self):
    self.config.line_width = 140
    self.source_str = """\
cmake_parse_arguments(ARG
                "SILENT" # optional keywords
                "" # one value keywords
                "" # multi value keywords
                ${ARGN})
"""
    self.expect_format = """\
cmake_parse_arguments(
  ARG
  "SILENT" # optional keywords
  "" # one value keywords
  "" # multi value keywords
  ${ARGN})
"""

  def test_format_off(self):
    self.source_str = """\
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
"""
    self.expect_format = """\
# This part of the comment should be formatted but...
# cmake-format: off
# This bunny should remain untouched:
# . 　 ＿　∩
# 　　ﾚﾍヽ| |
# 　　　 (・ｘ・)
# 　　 c( uu}
# cmake-format: on
# while this part should be formatted again
"""

  def test_todo_preserved(self):
    self.source_str = """\
# This is a comment
# that should be joined but
# TODO(josh): This todo should not be joined with the previous line.
# NOTE(josh): Also this should not be joined with the todo.
"""
    self.expect_format = """\
# This is a comment that should be joined but
# TODO(josh): This todo should not be joined with the previous line.
# NOTE(josh): Also this should not be joined with the todo.
"""

  def test_always_wrap(self):
    self.source_str = """\
foo(nonkwarg_a HEADERS a.h SOURCES a.cc DEPENDS foo)
"""

    with self.subTest(always_wrap=False):
      # assert_format(self, self.source_str)
      pass

    self.config.always_wrap = ['foo']
    with self.subTest(always_wrap=True):
      assert_format(self, self.source_str, """\
foo(nonkwarg_a
    HEADERS a.h
    SOURCES a.cc
    DEPENDS foo)
""")

  def test_preserve_separator(self):
    self.source_str = """\
# --------------------
# This is some
# text that I expect
# to reflow
# --------------------
"""
    self.expect_format = """\
# --------------------
# This is some text that I expect to reflow
# --------------------
"""
    with self.subTest(sub="a"):
      assert_format(self, self.source_str, self.expect_format)

    self.source_str = """\
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
# This is some
# text that I expect
# to reflow
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
"""
    self.expect_format = """\
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
# This is some text that I expect to reflow
# !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
"""

    with self.subTest(sub="b"):
      assert_format(self, self.source_str, self.expect_format)

    self.source_str = """\
# ----Not Supported----
# This is some
# text that I expect
# to reflow
# ----Not Supported----
"""
    self.expect_format = """\
# ----Not Supported----
# This is some text that I expect to reflow
# ----Not Supported----
"""

    with self.subTest(sub="c"):
      assert_format(self, self.source_str, self.expect_format)

  def test_bullets(self):
    self.source_str = """\
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
"""
    self.expect_format = """\
# This is a bulleted list:
#
# * item 1
# * item 2 this line gets merged with item 2
# * item 3 is really long and needs to be wrapped to a second line because it
#   wont all fit on one line without wrapping.
#
# But the list has ended and this line is free. And * this is not a bulleted
# list * and it will be * merged
"""

  def test_enum_lists(self):
    self.source_str = """\
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
"""
    self.expect_format = """\
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
"""

  def test_long_comment_after_command(self):
    self.source_str = """\
foo_command() # this is a long comment that exceeds the desired page width and will be wrapped to a newline
"""
    self.expect_format = """\
foo_command() # this is a long comment that exceeds the desired page width and
              # will be wrapped to a newline
"""

  def test_arg_just_fits(self):
    """
    Ensure that if an argument *just* fits that it isn't superfluously wrapped
"""

    self.source_str = """\
message(FATAL_ERROR "81 character line ----------------------------------------")
"""
    self.expect_format = """\
message(
  FATAL_ERROR "81 character line ----------------------------------------")
"""
    with self.subTest():
      assert_format(self, self.source_str, self.expect_format)

    self.source_str = """\
message(FATAL_ERROR
        "100 character line ----------------------------------------------------------"
) # Closing parenthesis is indented one space!
"""

    self.expect_format = """\
message(
  FATAL_ERROR
    "100 character line ----------------------------------------------------------"
) # Closing parenthesis is indented one space!
"""
    with self.subTest():
      assert_format(self, self.source_str, self.expect_format)

    self.source_str = """\
message(
  "100 character line ----------------------------------------------------------------------"
) # Closing parenthesis is indented one space!
"""

    self.expect_format = """\
message(
  "100 character line ----------------------------------------------------------------------"
) # Closing parenthesis is indented one space!
"""

    with self.subTest():
      assert_format(self, self.source_str, self.expect_format)
    self.source_str = self.expect_format = None

  def test_dangle_parens(self):
    self.config.dangle_parens = True
    self.config.max_subargs_per_line = 6

    with self.subTest():
      assert_format(self, """\
foo_command()
foo_command(arg1)
foo_command(arg1) # comment
""", """\
foo_command()
foo_command(arg1)
foo_command(arg1) # comment
""")

    with self.subTest():
      assert_format(self, """\
some_long_command_name(longargname longargname longargname longargname longargname)
""", """\
some_long_command_name(
  longargname longargname longargname longargname longargname
)
""")

    with self.subTest():
      assert_format(self, """\
if(foo)
  some_long_command_name(longargname longargname longargname longargname longargname)
endif()
""", """\
if(foo)
  some_long_command_name(
    longargname longargname longargname longargname longargname
  )
endif()
""")

    with self.subTest():
      assert_format(self, """\
some_long_command_name(longargname longargname longargname longargname longargname longargname longargname longargname)
""", """\
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
""")

    with self.subTest():
      assert_format(self, """\
target_include_directories(target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)
""", """\
target_include_directories(
  target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
)
""")

  def test_windows_line_endings_input(self):
    self.source_str = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

    self.expect_format = """\
#[[*********************************************
* Information line 1
* Information line 2
************************************************]]
"""

  def test_windows_line_endings_output(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'windows'
    self.config = configuration.Configuration(**config_dict)

    self.source_str = """\
#[[*********************************************
* Information line 1
* Information line 2
************************************************]]"""

    self.expect_format = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

  def test_auto_line_endings(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'auto'
    self.config = configuration.Configuration(**config_dict)

    self.source_str = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

    self.expect_format = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

  def test_keyword_case(self):
    config_dict = self.config.as_dict()
    config_dict['keyword_case'] = 'upper'
    self.config = configuration.Configuration(**config_dict)

    with self.subTest():
      assert_format(self, """\
foo(bar baz)
""", """\
foo(BAR BAZ)
""")

    config_dict = self.config.as_dict()
    config_dict['keyword_case'] = 'lower'
    self.config = configuration.Configuration(**config_dict)

    with self.subTest():
      assert_format(self, """\
foo(bar baz)
""", """\
foo(bar baz)
""")

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'unchanged'
    self.config = configuration.Configuration(**config_dict)
    with self.subTest():
      assert_format(self, """\
foo(BaR bAz)
""", """\
foo(bar baz)
""")

  def test_command_case(self):
    with self.subTest():
      assert_format(self, """\
FOO(bar baz)
""", """\
foo(bar baz)
""")

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'upper'
    self.config = configuration.Configuration(**config_dict)
    with self.subTest():
      assert_format(self, """\
foo(bar baz)
""", """\
FOO(bar baz)
""")

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'unchanged'
    self.config = configuration.Configuration(**config_dict)
    with self.subTest():
      assert_format(self, """\
FoO(bar baz)
""", """\
FoO(bar baz)
""")

  def test_comment_in_kwarg(self):
    self.source_str = """\
install(TARGETS foob
        ARCHIVE DESTINATION foobar
        # this is a line comment, not a comment on foobar
        COMPONENT baz)
"""
    self.expect_format = """\
install(
  TARGETS foob
  ARCHIVE DESTINATION foobar # this is a line comment, not a comment on foobar
          COMPONENT baz)
"""

  def test_elseif_else_control_space(self):
    self.config.separate_ctrl_name_with_space = True
    self.source_str = """\
if(foo)
elseif(bar)
else()
endif()
"""
    self.expect_format = """\
if (foo)

elseif (bar)

else ()

endif ()
"""

  def test_literal_first_comment(self):
    self.source_str = """\
# This comment
# is reflowed

# This comment
# is reflowed
"""
    self.expect_format = """\
# This comment is reflowed

# This comment is reflowed
"""

    self.config.first_comment_is_literal = True
    self.source_str = """\
# This comment
# is not reflowed

# This comment
# is reflowed
"""
    self.expect_format = """\
# This comment
# is not reflowed

# This comment is reflowed
"""

  def test_preserve_copyright(self):
    self.source_str = """\
# Copyright 2018: Josh Bialkowski
# This text should not be reflowed
# because it's a copyright
"""
    self.expect_format = """\
# Copyright 2018: Josh Bialkowski This text should not be reflowed because it's
# a copyright
"""

    self.config.literal_comment_pattern = " Copyright.*"
    self.source_str = """\
# Copyright 2018: Josh Bialkowski
# This text should not be reflowed
# because it's a copyright
"""
    self.expect_format = """\
# Copyright 2018: Josh Bialkowski
# This text should not be reflowed
# because it's a copyright
"""

  def test_byte_order_mark(self):
    self.source_str = """\
\ufeffcmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""
    self.expect_format = """\
cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

    self.config.emit_byteorder_mark = True
    self.source_str = """\
cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""
    self.expect_format = """\
\ufeffcmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

  def test_percommand_override(self):
    self.source_str = """\
FoO(bar baz)
"""
    self.expect_format = """\
foo(bar baz)
"""

    self.config.per_command["foo"] = {
        "command_case": "unchanged"
    }
    self.source_str = """\
FoO(bar baz)
"""
    self.expect_format = """\
FoO(bar baz)
"""

  def test_keyword_comment(self):
    self.source_str = """\
find_package(package REQUIRED
             COMPONENTS # --------------------------------------
                        # @TODO: This has to be filled manually
                        # --------------------------------------
                        this_is_a_really_long_word_foo)
"""

    self.expect_format = """\
find_package(
  package REQUIRED
  COMPONENTS # --------------------------------------
             # @TODO: This has to be filled manually
             # --------------------------------------
             this_is_a_really_long_word_foo)
"""

  def test_example_file(self):
    thisdir = os.path.dirname(__file__)
    infile_path = os.path.join(thisdir, '..', 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, '..', 'test', 'test_out.cmake')

    with io.open(infile_path, 'r', encoding='utf8') as infile:
      infile_text = infile.read()
    with io.open(outfile_path, 'r', encoding='utf8') as outfile:
      outfile_text = outfile.read()

    self.source_str = infile_text
    self.expect_format = outfile_text

  def test_one_char_short_hpack_rparen_case(self):
    # This was a particularly rare edge case. The situation is that the
    # the arguments are one character shy of fitting in the configured line
    # width, the statement column is the same as the indent column, and
    # all the arguments are positional. The problem was that the hpack if
    # possible logic did not account for the final paren. A fix is in place.
    self.config.line_width = 132
    self.config.tab_size = 4
    self.source_str = """
set(cubepp_HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
    ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)
"""
    self.expect_format = """\
set(cubepp_HDRS ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
                ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)
"""

  def test_layout_passes(self):
    self.config.layout_passes = {
      "StatementNode": [(0, True)],
      "ArgGroupNode": [(0, True)],
      "PargGroupNode": [(0, True)],
    }
    self.expect_format = """\
add_library(
  foobar
  STATIC
  sourcefile_01.cc
  sourcefile_02.cc)
"""

  def test_rulers_preserved_without_markup(self):
    self.config.enable_markup = False
    self.source_str = """
#########################################################################
# Custom targets
#########################################################################
"""
    self.expect_format = """\
#########################################################################
# Custom targets
#########################################################################
"""

  def test_comment_hashrulers(self):
    self.config.line_width = 74
    with self.subTest():
      assert_format(self, """
##################
# This comment has a long block before it.
#############
""", """\
# ########################################################################
# This comment has a long block before it.
# ########################################################################
""")

    with self.subTest():
      assert_format(self, """
###############################################
# This is a section in the CMakeLists.txt file.
############
# This stuff below here
#     should get re-flowed like
# normal comments.  Across multiple
# lines and
#             beyond.
""", """\
# ########################################################################
# This is a section in the CMakeLists.txt file.
# ########################################################################
# This stuff below here should get re-flowed like normal comments.  Across
# multiple lines and beyond.
""")

    # verify the original behavior is as described (they truncate to one #)
    self.config.hashruler_min_length = 1000
    with self.subTest():
      assert_format(self, """
##########################################################################
# This comment has a long block before it.
##########################################################################
""", """\
#
# This comment has a long block before it.
#
""")

    with self.subTest():
      assert_format(self, """
##########################################################################
# This is a section in the CMakeLists.txt file.
##########################################################################
# This stuff below here
#     should get re-flowed like
# normal comments.  Across multiple
# lines and
#             beyond.
""", """\
#
# This is a section in the CMakeLists.txt file.
#
# This stuff below here should get re-flowed like normal comments.  Across
# multiple lines and beyond.
""")

    # make sure changing hashruler_min_length works correctly
    # self.config.enable_markup = False
    for min_width in {3, 5, 7, 9}:
      self.config.hashruler_min_length = min_width

      # NOTE(josh): these tests use short rulers that wont be picked up by
      # the default pattern
      self.config.ruler_pattern = (r'#{%d}#*' % (min_width - 1))

      just_shy = '#' * (min_width - 1)
      just_right = '#' * min_width
      longer = '#' * (min_width + 2)
      full_line = '#' * (self.config.line_width - 2)

      assert_format(self, """
# A comment: min_width={min_width}, just_shy
{just_shy}
""".format(min_width=min_width, just_shy=just_shy),
          """\
# A comment: min_width={min_width}, just_shy
#
""".format(min_width=min_width))

      assert_format(self, """
# A comment: min_width={min_width}, just_right
{just_right}
""".format(min_width=min_width, just_right=just_right),
          """\
# A comment: min_width={min_width}, just_right
# {full_line}
""".format(min_width=min_width, full_line=full_line))

      assert_format(self, """
# A comment: min_width={min_width}, longer
{longer}
""".format(min_width=min_width, longer=longer),
          """\
# A comment: min_width={min_width}, longer
# {full_line}
""".format(min_width=min_width, full_line=full_line))


if __name__ == '__main__':
  unittest.main()
