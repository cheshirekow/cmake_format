# pylint: disable=bad-continuation
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestFileCommands(TestBase):
  """
  Test various examples of the file command
  """

  def test_file_write(self):
    self.source_str = r"""
file(WRITE ${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
     "include(CMakeFindDependencyMacro)\n"
     "include(\${X}/${CMAKE_PROJECT_NAME}Targets.cmake)\n")
"""

    self.expect_parse = [
      (NodeType.BODY, [
        (NodeType.WHITESPACE, []),
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
