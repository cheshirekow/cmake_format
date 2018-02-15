# -*- coding: utf-8 -*-
import os
import difflib
import unittest
import StringIO

from cmake_format import __main__
from cmake_format import commands
from cmake_format import configuration


def strip_indent(content, indent=6):
  """
  Strings used in this file are indented by 6-spaces to keep them readable
  within the python code that they are embedded. Remove those 6-spaces from
  the front of each line before running the tests.
  """
  return '\n'.join([line[indent:] for line in content.splitlines()])


class TestCanonicalFormatting(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(TestCanonicalFormatting, self).__init__(*args, **kwargs)
    self.config = configuration.Configuration()

  def setUp(self):
    commands.decl_command(self.config.fn_spec,
                          'foo', flags=['BAR', 'BAZ'], kwargs={
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

    infile = StringIO.StringIO(input_str)
    outfile = StringIO.StringIO()
    __main__.process_file(self.config, infile, outfile)
    delta_lines = list(difflib.unified_diff(outfile.getvalue().split('\n'),
                                            output_str.split('\n')))
    delta = '\n'.join(delta_lines[2:])

    if outfile.getvalue() != output_str:
      message = ('Input text:\n-----------------\n{}\n'
                 'Output text:\n-----------------\n{}\n'
                 'Expected Output:\n-----------------\n{}'
                 'Diff:\n-----------------\n{}'
                 .format(input_str, outfile.getvalue(), output_str, delta))
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

  def test_comment_after_closing_statement(self):
    self.do_format_test("""\
      if(True)
        message(STATUS "Lorem ipsum dolor sit amet, consectetur adipiscing elit")
      endif() # Short comment
      """, """\
      if(True)
        message(STATUS "Lorem ipsum dolor sit amet, consectetur adipiscing elit")
      endif() # Short comment
      """)

    self.do_format_test("""\
      if(True)
        message(STATUS "Lorem ipsum dolor sit amet, consectetur adipiscing elit")
      endif() # Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
      """, """\
      if(True)
        message(STATUS "Lorem ipsum dolor sit amet, consectetur adipiscing elit")
      endif() # Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              # eiusmod tempor incididunt
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

  def disabled_test_long_arg_on_newline(self):
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

  def disabled_test_long_kwargarg_on_newline(self):
    self.do_format_test("""\
      # This situation is similar but the argument to a KWARG needs to be on a
      # newline instead.
      set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")
      """, """\
      # This situation is similar but the argument to a KWARG needs to be on a
      # newline instead.
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
          DEPENDS foo bar baz)
      """)

  def test_some_string_stuff(self):
    self.do_format_test("""\
      # This command uses a string with escaped quote chars
      foo(some_arg some_arg "This is a \"string\" within a string")

      # This command uses an empty string
      foo(some_arg some_arg "")

      # This command uses a multiline string
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """, """\
      # This command uses a string with escaped quote chars
      foo(some_arg some_arg "This is a \"string\" within a string")

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
          #[==[This is a bracket comment at some nested level
          #    it is preserved verbatim, but trailing
          #    whitespace is removed.]==]
      """, """\
          #[==[This is a bracket comment at some nested level
          #    it is preserved verbatim, but trailing
          #    whitespace is removed.]==]
      """)

    # Make sure bracket comments are kept inline in their function call
    self.do_format_test("""\
      message("First Argument" #[[Bracket Comment]] "Second Argument")
      """, """\
      message("First Argument" #[[Bracket Comment]] "Second Argument")
      """)

  def test_dangling_parentheses(self):
    self.config.dangling_parentheses = True

    self.do_format_test("""\
      enable_testing()
      """, """\
      enable_testing()
      """)

    self.do_format_test("""\
      target_include_directories(target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)
      """, """\
      target_include_directories(
        target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
      )
      """)

    self.config.new_line_after_dangling_parentheses = True
    self.do_format_test("""\
      target_include_directories(target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)
      enable_testing()
      """, """\
      target_include_directories(
        target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
      )

      enable_testing()
      """)

    self.do_format_test("""\
      target_include_directories(
        target INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
      ) # FIXME no new line!
      """, """\
      target_include_directories(
        target INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>
      ) # FIXME no new line!
      """)

  def test_example_file(self):
    thisdir = os.path.dirname(__file__)
    infile_path = os.path.join(thisdir, 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, 'test', 'test_out.cmake')

    with open(infile_path, 'r') as infile:
      infile_text = infile.read()
    with open(outfile_path, 'r') as outfile:
      outfile_text = outfile.read()

    self.do_format_test(infile_text, outfile_text, strip_len=0)


if __name__ == '__main__':
  unittest.main()
