# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines

from __future__ import unicode_literals
import difflib
import io
import logging
import os
import sys
import unittest

from cmake_format import __main__
from cmake_format import configuration


def strip_indent(content, indent=6):
  """
  Strings used in this file are indented by 6-spaces to keep them readable
  within the python code that they are embedded. Remove those 6-spaces from
  the front of each line before running the tests.
  """

  # NOTE(josh): don't use splitlines() so that we get the same result
  # regardless of windows or unix line endings in content.
  return '\n'.join([line[indent:] for line in content.split('\n')])


class TestCanonicalFormatting(unittest.TestCase):
  """
  Given a bunch of example inputs, ensure that the output is as expected.
  """

  def __init__(self, *args, **kwargs):
    super(TestCanonicalFormatting, self).__init__(*args, **kwargs)
    self.config = configuration.Configuration()

  def setUp(self):
    self.config.fn_spec.add(
        'foo',
        flags=['BAR', 'BAZ'],
        kwargs={
            "HEADERS": '*',
            "SOURCES": '*',
            "DEPENDS": '*'
        })

  def tearDown(self):
    pass

  def do_format_test(self, input_str, output_str, strip_len=6):
    """
    Run the formatter on the input string and assert that the result matches
    the output string
    """

    input_str = strip_indent(input_str, strip_len)
    output_str = strip_indent(output_str, strip_len)

    if sys.version_info[0] < 3:
      assert isinstance(input_str, unicode)
    infile = io.StringIO(input_str)
    outfile = io.StringIO()

    __main__.process_file(self.config, infile, outfile)
    delta_lines = list(difflib.unified_diff(outfile.getvalue().split('\n'),
                                            output_str.split('\n')))
    delta = '\n'.join(delta_lines[2:])

    if outfile.getvalue() != output_str:
      message = ('Input text:\n-----------------\n{}\n'
                 'Output text:\n-----------------\n{}\n'
                 'Expected Output:\n-----------------\n{}\n'
                 'Diff:\n-----------------\n{}'
                 .format(input_str,
                         outfile.getvalue(),
                         output_str,
                         delta))
      if sys.version_info[0] < 3:
        message = message.encode('utf-8')
      raise AssertionError(message)

  def test_collapse_additional_newlines(self):
    self.do_format_test("""\
      # The following multiple newlines should be collapsed into a single newline




      cmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
      """, """\
      # The following multiple newlines should be collapsed into a single newline

      cmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
      """)

  def test_multiline_reflow(self):
    self.do_format_test("""\
      # This multiline-comment should be reflowed
      # into a single comment
      # on one line
      """, """\
      # This multiline-comment should be reflowed into a single comment on one line
      """)

  def test_comment_before_command(self):
    self.do_format_test("""\
      # This comment should remain right before the command call.
      # Furthermore, the command call should be formatted
      # to a single line.
      add_subdirectories(foo bar baz
        foo2 bar2 baz2)
      """, """\
      # This comment should remain right before the command call. Furthermore, the
      # command call should be formatted to a single line.
      add_subdirectories(foo bar baz foo2 bar2 baz2)
      """)

  def test_long_args_command_split(self):
    self.do_format_test("""\
      # This very long command should be split to multiple lines
      set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)
      """, """\
      # This very long command should be split to multiple lines
      set(HEADERS
          very_long_header_name_a.h
          very_long_header_name_b.h
          very_long_header_name_c.h)
      """)

  def test_lots_of_args_command_split(self):
    self.do_format_test("""\
      # This command should be split into one line per entry because it has a long
      # argument list.
      set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc source_g.cc)
      """, """\
      # This command should be split into one line per entry because it has a long
      # argument list.
      set(SOURCES
          source_a.cc
          source_b.cc
          source_d.cc
          source_e.cc
          source_f.cc
          source_g.cc)
      """)

  # TODO(josh): figure out why this test elicits different behavior than the
  # whole-file demo.
  def test_string_preserved_during_split(self):
    self.do_format_test("""\
      # The string in this command should not be split
      set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")
      """, """\
      # The string in this command should not be split
      set_target_properties(foo bar baz
                            PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")
      """)

  def test_long_arg_on_newline(self):
    self.do_format_test("""\
      # This command has a very long argument and can't be aligned with the command
      # end, so it should be moved to a new line with block indent + 1.
      some_long_command_name("Some very long argument that really needs to be on the next line.")
      """, """\
      # This command has a very long argument and can't be aligned with the command
      # end, so it should be moved to a new line with block indent + 1.
      some_long_command_name(
        "Some very long argument that really needs to be on the next line.")
      """)

  def test_long_kwargarg_on_newline(self):
    self.do_format_test("""\
      # This situation is similar but the argument to a KWARG needs to be on a
      # newline instead.
      set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
      """, """\
      # This situation is similar but the argument to a KWARG needs to be on a newline
      # instead.
      set(CMAKE_CXX_FLAGS
          "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
      """)

  def test_argcomment_preserved_and_reflowed(self):
    self.do_format_test("""\
      set(HEADERS header_a.h header_b.h # This comment should
                                        # be preserved, moreover it should be split
                                        # across two lines.
          header_c.h header_d.h)
      """, """\
      set(HEADERS
          header_a.h
          header_b.h # This comment should be preserved, moreover it should be split
                     # across two lines.
          header_c.h
          header_d.h)
      """)

  def test_argcomments_force_reflow(self):
    self.config.line_width = 140
    self.do_format_test("""\
      cmake_parse_arguments(ARG
                      "SILENT" # optional keywords
                      "" # one value keywords
                      "" # multi value keywords
                      ${ARGN})
    """, """\
      cmake_parse_arguments(ARG
                            "SILENT" # optional keywords
                            "" # one value keywords
                            "" # multi value keywords
                            ${ARGN})
    """)

  def test_format_off(self):
    self.do_format_test("""\
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
      """, """\
      # This part of the comment should be formatted but...
      # cmake-format: off
      # This bunny should remain untouched:
      # . 　 ＿　∩
      # 　　ﾚﾍヽ| |
      # 　　　 (・ｘ・)
      # 　　 c( uu}
      # cmake-format: on
      # while this part should be formatted again
      """)

  def test_paragraphs_preserved(self):
    self.do_format_test("""\
      # This is a paragraph
      #
      # This is a second paragraph
      #
      # This is a third paragraph
      """, """\
      # This is a paragraph
      #
      # This is a second paragraph
      #
      # This is a third paragraph
      """)

  def test_todo_preserved(self):
    self.do_format_test("""\
      # This is a comment
      # that should be joined but
      # TODO(josh): This todo should not be joined with the previous line.
      # NOTE(josh): Also this should not be joined with the todo.
      """, """\
      # This is a comment that should be joined but
      # TODO(josh): This todo should not be joined with the previous line.
      # NOTE(josh): Also this should not be joined with the todo.
      """)

  def test_complex_nested_stuff(self):
    self.do_format_test("""\
      if(foo)
      if(sbar)
      # This comment is in-scope.
      add_library(foo_bar_baz foo.cc bar.cc # this is a comment for arg2
                    # this is more comment for arg2, it should be joined with the first.
          baz.cc) # This comment is part of add_library

      other_command(some_long_argument some_long_argument) # this comment is very long and gets split across some lines

      other_command(some_long_argument some_long_argument some_long_argument) # this comment is even longer and wouldn't make sense to pack at the end of the command so it gets it's own lines
      endif()
      endif()
      """, """\
      if(foo)
        if(sbar)
          # This comment is in-scope.
          add_library(foo_bar_baz
                      foo.cc
                      bar.cc # this is a comment for arg2 this is more comment for
                             # arg2, it should be joined with the first.
                      baz.cc) # This comment is part of add_library

          other_command(some_long_argument some_long_argument) # this comment is very
                                                               # long and gets split
                                                               # across some lines

          other_command(some_long_argument some_long_argument some_long_argument)
          # this comment is even longer and wouldn't make sense to pack at the end of
          # the command so it gets it's own lines
        endif()
      endif()
      """)

  def test_custom_command(self):
    self.do_format_test("""\
      # This very long command should be broken up along keyword arguments
      foo(nonkwarg_a nonkwarg_b HEADERS a.h b.h c.h d.h e.h f.h SOURCES a.cc b.cc d.cc DEPENDS foo bar baz)
      """, """\
      # This very long command should be broken up along keyword arguments
      foo(nonkwarg_a nonkwarg_b
          HEADERS a.h
                  b.h
                  c.h
                  d.h
                  e.h
                  f.h
          SOURCES a.cc b.cc d.cc
          DEPENDS foo
          bar baz)
      """)

  def test_always_wrap(self):
    self.do_format_test("""\
      foo(nonkwarg_a HEADERS a.h SOURCES a.cc DEPENDS foo)
      """, """\
      foo(nonkwarg_a HEADERS a.h SOURCES a.cc DEPENDS foo)
      """)
    self.config.always_wrap = ['foo']
    self.do_format_test("""\
      foo(nonkwarg_a HEADERS a.h SOURCES a.cc DEPENDS foo)
      """, """\
      foo(nonkwarg_a
          HEADERS a.h
          SOURCES a.cc
          DEPENDS foo)
      """)

  def test_multiline_string(self):
    self.do_format_test("""\
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """, """\
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """)

  def test_some_string_stuff(self):
    self.do_format_test("""\
      # This command uses a string with escaped quote chars
      foo(some_arg some_arg "This is a \\"string\\" within a string")

      # This command uses an empty string
      foo(some_arg some_arg "")

      # This command uses a multiline string
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """, """\
      # This command uses a string with escaped quote chars
      foo(some_arg some_arg "This is a \\"string\\" within a string")

      # This command uses an empty string
      foo(some_arg some_arg "")

      # This command uses a multiline string
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """)

  def test_format_off_code(self):
    self.do_format_test("""\
      # No, I really want this to look ugly
      # cmake-format: off
      add_library(a b.cc
        c.cc         d.cc
                e.cc)
      # cmake-format: on
      """, """\
      # No, I really want this to look ugly
      # cmake-format: off
      add_library(a b.cc
        c.cc         d.cc
                e.cc)
      # cmake-format: on
      """)

  def test_multiline_statement_comment_idempotent(self):
    self.do_format_test("""\
      set(HELLO hello world!) # TODO(josh): fix this bad code with some change that
                              # takes mutiple lines to explain
      """, """\
      set(HELLO hello world!) # TODO(josh): fix this bad code with some change that
                              # takes mutiple lines to explain
      """)

  def test_nested_parens(self):
    self.do_format_test("""\
      if((NOT HELLO) OR (NOT EXISTS ${WORLD}))
        message(WARNING "something is wrong")
        set(foobar FALSE)
      endif()
      """, """\
      if((NOT HELLO) OR (NOT EXISTS ${WORLD}))
        message(WARNING "something is wrong")
        set(foobar FALSE)
      endif()
      """)

  def test_function_def(self):
    self.do_format_test("""\
      function(forbarbaz arg1)
        do_something(arg1 ${ARGN})
      endfunction()
      """, """\
      function(forbarbaz arg1)
        do_something(arg1 ${ARGN})
      endfunction()
      """)

  def test_macro_def(self):
    self.do_format_test("""\
      macro(forbarbaz arg1)
        do_something(arg1 ${ARGN})
      endmacro()
      """, """\
      macro(forbarbaz arg1)
        do_something(arg1 ${ARGN})
      endmacro()
      """)

  def test_foreach(self):
    self.do_format_test("""\
      foreach(forbarbaz arg1 arg2, arg3)
        message(hello ${foobarbaz})
      endforeach()
      """, """\
      foreach(forbarbaz arg1 arg2, arg3)
        message(hello ${foobarbaz})
      endforeach()
      """)

  def test_while(self):
    self.do_format_test("""\
      while(forbarbaz arg1 arg2, arg3)
        message(hello ${foobarbaz})
      endwhile()
      """, """\
      while(forbarbaz arg1 arg2, arg3)
        message(hello ${foobarbaz})
      endwhile()
      """)

  def test_ctrl_space(self):
    self.config.separate_ctrl_name_with_space = True
    self.do_format_test("""\
      if(foo)
        myfun(foo bar baz)
      endif()
      """, """\
      if (foo)
        myfun(foo bar baz)
      endif ()
      """)

  def test_fn_space(self):
    self.config.separate_fn_name_with_space = True
    self.do_format_test("""\
      myfun(foo bar baz)
      """, """\
      myfun (foo bar baz)
      """)

  def test_preserve_separator(self):
    self.do_format_test("""\
      # --------------------
      # This is some
      # text that I expect
      # to reflow
      # --------------------
      """, """\
      # --------------------
      # This is some text that I expect to reflow
      # --------------------
      """)

    self.do_format_test("""\
      # !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
      # This is some
      # text that I expect
      # to reflow
      # !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
      """, """\
      # !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
      # This is some text that I expect to reflow
      # !@#$^&*!@#$%^&*!@#$%^&*!@#$%^&*
      """)

    self.do_format_test("""\
      # ----Not Supported----
      # This is some
      # text that I expect
      # to reflow
      # ----Not Supported----
      """, """\
      # ----Not Supported----
      # This is some text that I expect to reflow
      # ----Not Supported----
      """)

  def test_bullets(self):
    self.do_format_test("""\
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
      """, """\
      # This is a bulleted list:
      #
      # * item 1
      # * item 2 this line gets merged with item 2
      # * item 3 is really long and needs to be wrapped to a second line because it
      #   wont all fit on one line without wrapping.
      #
      # But the list has ended and this line is free. And * this is not a bulleted
      # list * and it will be * merged
      """)

  def test_enum_lists(self):
    self.do_format_test("""\
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
      """, """\
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
      """)

  def test_nested_bullets(self):
    self.do_format_test("""\
      # This is a bulleted list:
      #
      #   * item 1
      #   * item 2
      #
      #     * item 3
      #     * item 4
      #
      #       * item 5
      #       * item 6
      #
      # * item 7
      # * item 8
      """, """\
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
      """)

  def test_comment_fence(self):
    self.do_format_test("""\
      # ~~~~~~
      #   This is some
      #  verbatim text
      #      that should not be
      # formatted
      # ```````
      """, """\
      # ~~~
      #   This is some
      #  verbatim text
      #      that should not be
      # formatted
      # ~~~
      """)

  def test_bracket_comments(self):

    self.do_format_test("""\
      #[[This is a bracket comment.
      It is preserved verbatim, but trailing whitespace is removed.
      So things like --this-- Are fine:]]
      """, """\
      #[[This is a bracket comment.
      It is preserved verbatim, but trailing whitespace is removed.
      So things like --this-- Are fine:]]
      """)

    self.do_format_test("""\
      if(foo)
        #[==[This is a bracket comment at some nested level
        #    it is preserved verbatim, but trailing
        #    whitespace is removed.]==]
      endif()
      """, """\
      if(foo)
        #[==[This is a bracket comment at some nested level
        #    it is preserved verbatim, but trailing
        #    whitespace is removed.]==]
      endif()
      """)

    # Make sure bracket comments are kept inline in their function call
    self.do_format_test("""\
      message("First Argument" #[[Bracket Comment]] "Second Argument")
      """, """\
      message("First Argument" #[[Bracket Comment]] "Second Argument")
      """)

  def test_comment_after_command(self):
    self.do_format_test("""\
      foo_command() # comment
    """, """\
      foo_command() # comment
    """)

    self.do_format_test("""\
      foo_command() # this is a long comment that exceeds the desired page width and will be wrapped to a newline
    """, """\
      foo_command() # this is a long comment that exceeds the desired page width and
                    # will be wrapped to a newline
    """)

  def test_arg_just_fits(self):
    """
    Ensure that if an argument *just* fits that it isn't superfluously wrapped
    """

    self.do_format_test("""\
      message(FATAL_ERROR "81 character line ----------------------------------------")
    """, """\
      message(
        FATAL_ERROR "81 character line ----------------------------------------")
    """)

    self.do_format_test("""\
      message(FATAL_ERROR
              "100 character line ----------------------------------------------------------"
      ) # Closing parenthesis is indented one space!
    """, """\
      message(
        FATAL_ERROR
          "100 character line ----------------------------------------------------------"
        ) # Closing parenthesis is indented one space!
    """)

    self.do_format_test("""\
      message(
        "100 character line ----------------------------------------------------------------------"
        ) # Closing parenthesis is indented one space!
    """, """\
      message(
        "100 character line ----------------------------------------------------------------------"
        ) # Closing parenthesis is indented one space!
    """)

  def test_dangle_parens(self):
    self.config.dangle_parens = True
    self.config.max_subargs_per_line = 6
    self.do_format_test("""\
      foo_command()
      foo_command(arg1)
      foo_command(arg1) # comment
    """, """\
      foo_command()
      foo_command(arg1)
      foo_command(arg1) # comment
    """)

    self.do_format_test("""\
      some_long_command_name(longargname longargname longargname longargname longargname)
    """, """\
      some_long_command_name(
        longargname longargname longargname longargname longargname
      )
    """)

    self.do_format_test("""\
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

    self.do_format_test("""\
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

    self.do_format_test("""\
      target_include_directories(target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)
      """, """\
      target_include_directories(
        target
        INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
      )
      """)

  def test_windows_line_endings_input(self):
    self.do_format_test(
        "      #[[*********************************************\r\n"
        "      * Information line 1\r\n"
        "      * Information line 2\r\n"
        "      ************************************************]]\r\n", """\
      #[[*********************************************
      * Information line 1
      * Information line 2
      ************************************************]]\n""")

  def test_windows_line_endings_output(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'windows'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test(
        """\
      #[[*********************************************
      * Information line 1
      * Information line 2
      ************************************************]]""",
        "      #[[*********************************************\r\n"
        "      * Information line 1\r\n"
        "      * Information line 2\r\n"
        "      ************************************************]]\r\n")

  def test_auto_line_endings(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'auto'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test(
        "      #[[*********************************************\r\n"
        "      * Information line 1\r\n"
        "      * Information line 2\r\n"
        "      ************************************************]]\r\n",
        "      #[[*********************************************\r\n"
        "      * Information line 1\r\n"
        "      * Information line 2\r\n"
        "      ************************************************]]\r\n")

  def test_keyword_case(self):
    config_dict = self.config.as_dict()
    config_dict['keyword_case'] = 'upper'
    self.config = configuration.Configuration(**config_dict)
    self.do_format_test(
        """\
      foo(bar baz)
      """, """\
      foo(BAR BAZ)
      """)

    config_dict = self.config.as_dict()
    config_dict['keyword_case'] = 'lower'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test(
        """\
      foo(bar baz)
      """, """\
      foo(bar baz)
      """)

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'unchanged'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test("""\
      foo(BaR bAz)
      """, """\
      foo(bar baz)
      """)

  def test_command_case(self):
    self.do_format_test(
        """\
      FOO(bar baz)
      """, """\
      foo(bar baz)
      """)

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'upper'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test(
        """\
      foo(bar baz)
      """, """\
      FOO(bar baz)
      """)

    config_dict = self.config.as_dict()
    config_dict['command_case'] = 'unchanged'
    self.config = configuration.Configuration(**config_dict)

    self.do_format_test("""\
      FoO(bar baz)
      """, """\
      FoO(bar baz)
      """)

  def test_component(self):
    self.do_format_test("""\
      install(TARGETS ${PROJECT_NAME}
              EXPORT ${CMAKE_PROJECT_NAME}Targets
              ARCHIVE DESTINATION lib COMPONENT install-app
              LIBRARY DESTINATION lib COMPONENT install-app
              RUNTIME DESTINATION bin COMPONENT install-app)
      """, """\
      install(TARGETS ${PROJECT_NAME}
              EXPORT ${CMAKE_PROJECT_NAME}Targets
              ARCHIVE DESTINATION lib COMPONENT install-app
              LIBRARY DESTINATION lib COMPONENT install-app
              RUNTIME DESTINATION bin COMPONENT install-app)
      """)

  def test_comment_in_statement(self):
    self.do_format_test("""\
      add_library(foo
        # This comment is not attached to an argument
        foo.cc
        bar.cc)
      """, """\
      add_library(foo
                  # This comment is not attached to an argument
                  foo.cc bar.cc)
      """)

  def test_comment_at_end_of_statement(self):
    self.do_format_test("""\
      add_library(foo foo.cc bar.cc
                  # This comment is not attached to an argument
                  )
      """, """\
      add_library(foo foo.cc bar.cc
                  # This comment is not attached to an argument
                  )
      """)

    self.do_format_test("""\
      target_link_libraries(libraryname PUBLIC
                            ${COMMON_LIBRARIES}
                            # add more library dependencies here
                            )
      """, """\
      target_link_libraries(libraryname
                            PUBLIC ${COMMON_LIBRARIES}
                                   # add more library dependencies here
                            )
      """)

    self.do_format_test("""\
      find_package(foobar REQUIRED
                   COMPONENTS some_component
                              # some_other_component
                              # This is a very long comment, and actually the second comment in this row.
                   )
      """, """\
      find_package(foobar REQUIRED
                   COMPONENTS some_component
                              # some_other_component
                              # This is a very long comment, and actually the second
                              # comment in this row.
                   )
      """)

  def test_comment_in_kwarg(self):
    self.do_format_test("""\
      install(ARCHIVE DESTINATION foobar
              # this is a line comment, not a comment on foobar
              COMPONENT baz)
      """, """\
      install(ARCHIVE DESTINATION foobar
                      # this is a line comment, not a comment on foobar
                      COMPONENT baz)
      """)

  def test_complicated_boolean(self):
    self.config.max_subargs_per_line = 10
    self.do_format_test("""\
      set(matchme
          "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
      if (("${var}" MATCHES "_TEST_" AND NOT
            "${var}" MATCHES
            "${matchme}")
          OR (CONFIG_AV1_ENCODER AND CONFIG_ENCODE_PERF_TESTS AND
              "${var}" MATCHES "_ENCODE_PERF_TEST_")
          OR (CONFIG_AV1_DECODER AND CONFIG_DECODE_PERF_TESTS AND
              "${var}" MATCHES "_DECODE_PERF_TEST_")
          OR (CONFIG_AV1_ENCODER AND "${var}" MATCHES "_TEST_ENCODER_")
          OR (CONFIG_AV1_DECODER AND  "${var}" MATCHES "_TEST_DECODER_"))
        list(APPEND aom_test_source_vars ${var})
      endif ()
    """, """\
      set(matchme "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
      if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
         OR (CONFIG_AV1_ENCODER
             AND CONFIG_ENCODE_PERF_TESTS
             AND "${var}" MATCHES "_ENCODE_PERF_TEST_")
         OR (CONFIG_AV1_DECODER
             AND CONFIG_DECODE_PERF_TESTS
             AND "${var}" MATCHES "_DECODE_PERF_TEST_")
         OR (CONFIG_AV1_ENCODER AND "${var}" MATCHES "_TEST_ENCODER_")
         OR (CONFIG_AV1_DECODER AND "${var}" MATCHES "_TEST_DECODER_"))
        list(APPEND aom_test_source_vars ${var})
      endif()
    """)

  def test_algoorder_preference(self):
    self.config.max_subargs_per_line = 10
    self.do_format_test("""\
      some_long_command_name(longargument longargument longargument longargument
        longargument longargument)
      """, """\
      some_long_command_name(longargument longargument longargument longargument
                             longargument longargument)
      """)

    self.config.algorithm_order = [0, 2]
    self.do_format_test("""\
      some_long_command_name(longargument longargument longargument longargument
        longargument longargument)
      """, """\
      some_long_command_name(
        longargument longargument longargument longargument longargument longargument)
      """)

  def test_elseif(self):
    self.do_format_test("""\
      if(MSVC)

      elseif((CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
            OR CMAKE_COMPILER_IS_GNUCC
            OR CMAKE_COMPILER_IS_GNUCXX)

      endif()
    """, """\
      if(MSVC)

      elseif((CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
             OR CMAKE_COMPILER_IS_GNUCC
             OR CMAKE_COMPILER_IS_GNUCXX)

      endif()
    """)

  def test_elseif_else_control_space(self):
    self.config.separate_ctrl_name_with_space = True
    self.do_format_test("""\
      if(foo)
      elseif(bar)
      else()
      endif()
    """, """\
      if (foo)

      elseif (bar)

      else ()

      endif ()
    """)

  def test_disable_markup(self):
    self.config.enable_markup = False
    self.do_format_test("""\
      # don't reflow
      # or parse markup
      # for these lines
    """, """\
      # don't reflow
      # or parse markup
      # for these lines
    """)

  def test_literal_first_comment(self):
    self.do_format_test("""\
      # This comment
      # is reflowed

      # This comment
      # is reflowed
    """, """\
      # This comment is reflowed

      # This comment is reflowed
    """)

    self.config.first_comment_is_literal = True
    self.do_format_test("""\
      # This comment
      # is not reflowed

      # This comment
      # is reflowed
    """, """\
      # This comment
      # is not reflowed

      # This comment is reflowed
    """)

  def test_shebang_preserved(self):
    self.do_format_test("""\
      #!/usr/bin/cmake -P
    """, """\
      #!/usr/bin/cmake -P
    """)

  def test_preserve_copyright(self):
    self.do_format_test("""\
      # Copyright 2018: Josh Bialkowski
      # This text should not be reflowed
      # because it's a copyright
    """, """\
      # Copyright 2018: Josh Bialkowski This text should not be reflowed because it's
      # a copyright
    """)

    self.config.literal_comment_pattern = " Copyright.*"
    self.do_format_test("""\
      # Copyright 2018: Josh Bialkowski
      # This text should not be reflowed
      # because it's a copyright
    """, """\
      # Copyright 2018: Josh Bialkowski
      # This text should not be reflowed
      # because it's a copyright
    """)

  def test_kwarg_match_consumes(self):
    self.do_format_test("""\
      install(TARGETS myprog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT runtime)
    """, """\
      install(TARGETS myprog
              RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT
              runtime)
    """)

    self.do_format_test("""\
      add_test(NAME myTestName COMMAND testCommand --run_test=@quick)
    """, """\
      add_test(NAME myTestName COMMAND testCommand --run_test=@quick)
    """)

  def test_byte_order_mark(self):
    self.do_format_test("""\
      \ufeffcmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
      """, """\
      cmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
    """)

    self.config.emit_byteorder_mark = True
    self.do_format_test("""\
      cmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
      """, """\
      \ufeffcmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
    """)

  def test_percommand_override(self):
    self.do_format_test("""\
      FoO(bar baz)
      """, """\
      foo(bar baz)
      """)

    self.config.per_command["foo"] = {
        "command_case": "unchanged"
    }
    self.do_format_test("""\
      FoO(bar baz)
      """, """\
      FoO(bar baz)
      """)

  def test_quoted_assignment_literal(self):
    self.do_format_test("""\
      target_compile_definitions(foo PUBLIC BAR="Quoted String" BAZ_______________________Z)
      """, """\
      target_compile_definitions(foo
                                 PUBLIC
                                 BAR="Quoted String"
                                 BAZ_______________________Z)
      """)

  def test_example_file(self):
    thisdir = os.path.dirname(__file__)
    infile_path = os.path.join(thisdir, 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, 'test', 'test_out.cmake')

    with io.open(infile_path, 'r', encoding='utf8') as infile:
      infile_text = infile.read()
    with io.open(outfile_path, 'r', encoding='utf8') as outfile:
      outfile_text = outfile.read()

    self.do_format_test(infile_text, outfile_text, strip_len=0)

  def test_one_char_short_hpack_rparen_case(self):
    # This was a particularly rare edge case. The situation is that the
    # the arguments are one character shy of fitting in the configured line
    # width, the statement column is the same as the indent column, and
    # all the arguments are positional. The problem was that the hpack if
    # possible logic did not account for the final paren. A fix is in place.
    self.config.line_width = 132
    self.config.tab_size = 4
    self.do_format_test("""
      set(cubepp_HDRS
          ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
          ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)
    """, """\
      set(cubepp_HDRS ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/AppDelegate.h
          ${CMAKE_CURRENT_SOURCE_DIR}/macOS/cubepp/DemoViewController.h)
    """)


if __name__ == '__main__':
  format_str = '[%(levelname)-4s] %(filename)s:%(lineno)-3s: %(message)s'
  logging.basicConfig(level=logging.DEBUG,
                      format=format_str,
                      datefmt='%Y-%m-%d %H:%M:%S',
                      filemode='w')
  unittest.main()
