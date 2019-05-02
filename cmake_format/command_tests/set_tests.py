# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestSetCommand(TestBase):
  """
  Test various examples of the set() function
  """

  def test_parse(self):
    self.source_str = """\
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)
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
              (NodeType.COMMENT, []),
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

  def test_tag_ignored_if_autosort_disabled(self):
    self.config.autosort = False
    self.config.max_subargs_per_line = 10
    self.source_str = """\
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)
"""
    self.expect_format = """\
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)
"""

  def test_tag_respected_if_autosort_enabled(self):
    self.config.autosort = True
    self.config.max_subargs_per_line = 10
    self.source_str = """\
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)
"""
    self.expect_format = """\
set(SOURCES #[[cmf:sortable]] bar.cc baz.cc foo.cc)
"""

  def test_bracket_comment_is_not_trailing_comment_of_kwarg(self):
    self.config.autosort = True
    self.config.max_subargs_per_line = 3
    self.source_str = """\
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)
"""
    self.expect_format = """\
set(SOURCES
    #[[cmf:sortable]]
    bar.cc baz.cc foo.cc)
"""

  def test_bracket_comment_short_tag(self):
    self.config.autosort = True
    self.source_str = self.expect_format = """\
set(SOURCES
    #[[cmf:sort]]
    bar.cc baz.cc foo.cc)
"""

  def test_line_comment_long_tag(self):
    self.config.autosort = True
    self.source_str = self.expect_format = """\
set(sources
    # cmake-format: sortable
    bar.cc baz.cc foo.cc)
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
set(SOURCES
    source_a.cc
    source_b.cc
    source_d.cc
    source_e.cc
    source_f.cc
    source_g.cc)
"""


if __name__ == '__main__':
  unittest.main()
