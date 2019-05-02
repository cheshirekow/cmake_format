# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestFileCommands(TestBase):
  """
  Test various examples of the file command
  """

  def test_file_read(self):
    self.expect_format = """\
file(READ foobar.baz foobar_content)
"""

  def test_file_strings(self):
    self.expect_format = """\
file(STRINGS foobar.baz foorbar_content REGEX hello)
"""

  def test_file_hash(self):
    self.expect_format = """\
file(SHA1 foobar.baz foobar_digest)
"""

  def test_file_timestamp(self):
    self.expect_format = """\
file(TIMESTAMP foobar.baz foobar_timestamp)
"""

  def test_file_write(self):
    self.expect_format = """\
file(WRITE foobar.baz
     "first line of the output file long enough to force a wrap"
     "second line of the output file long enough to force a wrap")
"""

  def test_file_append(self):
    self.expect_format = """\
file(APPEND foobar.baz
     "first line of the output file long enough to force a wrap"
     "second line of the output file long enough to force a wrap")
"""

  def test_file_generate_output(self):
    self.expect_format = """\
file(GENERATE
     OUTPUT foobar.baz
     CONTENT "file content line one" #
             "file content line two"
             "file content line three"
     CONDITION (FOO AND BAR) OR BAZ)
"""

  def test_file_glob(self):
    self.expect_format = """\
file(GLOB globout RELATIVE foo/bar/baz "*.py" "*.txt")
"""

  def test_file_copy(self):
    self.expect_format = r"""
file(COPY foo bar baz
     DESTINATION foobar
     FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
     FILES_MATCHING
     PATTERN "*.h"
     REGEX ".*\\.cc")
"""[1:]

  def test_file_write_a(self):
    self.expect_parse = [
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

    self.expect_format = r"""
file(WRITE ${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
     "include(CMakeFindDependencyMacro)\n"
     "include(\${X}/${CMAKE_PROJECT_NAME}Targets.cmake)\n")
"""[1:]


if __name__ == '__main__':
  unittest.main()
