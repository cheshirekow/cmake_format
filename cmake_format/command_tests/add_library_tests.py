# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestAddLibraryCommand(TestBase):
  """
  Test various examples of add_library()
  """

  def test_single_argument(self):
    self.source_str = """\
add_library(foobar foo.cc)
"""

    self.expect_parse = [
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

    self.expect_format = """\
add_library(foobar foo.cc)
"""

  def test_all_arguments(self):
    self.source_str = """\
add_library(foobar STATIC EXCLUDE_FROM_ALL sourcefile_01.cc
  sourcefile_02.cc sourcefile_03.cc sourcefile_04.cc sourcefile_05.cc
  sourcefile_06.cc sourcefile_07.cc)
"""

    self.expect_parse = [
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

    self.expect_format = """\
add_library(foobar STATIC EXCLUDE_FROM_ALL
            sourcefile_01.cc
            sourcefile_02.cc
            sourcefile_03.cc
            sourcefile_04.cc
            sourcefile_05.cc
            sourcefile_06.cc
            sourcefile_07.cc)
"""

  def test_parse_with_concluding_comments(self):
    self.source_str = """\
add_library(foo STATIC EXCLUDE_FROM_ALL foo.cc bar.cc
            # This is a concluding comment
            )
"""
    self.expect_parse = [
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
            ]),
            (NodeType.COMMENT, []),
          ]),
          (NodeType.RPAREN, []),
        ]),
        (NodeType.WHITESPACE, []),
      ]),
    ]

  def test_sort_arguments(self):
    self.config.autosort = True
    self.source_str = """\
add_library(foobar STATIC sourcefile_04.cc
  sourcefile_03.cc sourcefile_01.cc sourcefile_02.cc)
"""

    self.expect_format = """\
add_library(foobar STATIC
            sourcefile_01.cc
            sourcefile_02.cc
            sourcefile_03.cc
            sourcefile_04.cc)
"""

  def test_disable_autosort_with_tag(self):
    self.config.autosort = True
    self.source_str = """\
add_library(foobar STATIC # cmake-format: unsort
  sourcefile_04.cc sourcefile_03.cc sourcefile_01.cc sourcefile_02.cc)
"""

    self.expect_format = """\
add_library(foobar STATIC
            # cmake-format: unsort
            sourcefile_04.cc
            sourcefile_03.cc
            sourcefile_01.cc
            sourcefile_02.cc)
"""

  def test_imported_form(self):
    self.config.max_subargs_per_line = 5
    self.expect_format = """\
add_library(foobar SHARED IMPORTED GLOBAL)
"""
    self.expect_parse = [
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

  def test_object_form(self):
    self.expect_format = """\
add_library(foobar OBJECT bar.cc baz.cc foo.cc)
"""
    self.expect_parse = [
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

  def test_alias_form(self):
    self.expect_format = """\
add_library(foobar ALIAS foobarbaz)
"""
    self.expect_parse = [
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

  def test_interface_form(self):
    self.config.max_subargs_per_line = 5
    self.expect_format = """\
add_library(foobar INTERFACE IMPORTED GLOBAL)
"""
    self.expect_parse = [
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

  def test_descriminator_hidden_behind_variable(self):
    self.config.max_subargs_per_line = 5
    self.expect_format = """\
set(libtype OBJECT)
add_library(foobar ${libtype} ${alpha}.cc bar.cc baz.cc foo.cc)
"""


if __name__ == '__main__':
  unittest.main()
