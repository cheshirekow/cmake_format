# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parse.common import NodeType


class TestAddLibraryCommand(TestBase):
  """
  Test various examples of add_library()
  """
  kExpectNumSidecarTests = 9

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
add_library(foobar STATIC sourcefile_01.cc sourcefile_02.cc sourcefile_03.cc
                          sourcefile_04.cc)
"""


if __name__ == '__main__':
  unittest.main()
