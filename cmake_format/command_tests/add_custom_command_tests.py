# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestAddCustomCommand(TestBase):
  """
  Test various examples of add_custom_command()
  """

  def test_single_argument(self):
    self.source_str = """\
 add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
                    COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
                            ${CMAKE_CURRENT_BINARY_DIR}
                    COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
                    DEPENDS ${foobar_docs}
                    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
"""

    self.expect_parse = [
      (NodeType.BODY, [
        (NodeType.WHITESPACE, []),
        (NodeType.STATEMENT, [
          (NodeType.FUNNAME, []),
          (NodeType.LPAREN, []),
          (NodeType.ARGGROUP, [
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.ARGGROUP, [
                (NodeType.PARGGROUP, [
                  (NodeType.ARGUMENT, []),
                ]),
                (NodeType.FLAGGROUP, [
                  (NodeType.FLAG, []),
                ]),
                (NodeType.PARGGROUP, [
                  (NodeType.ARGUMENT, []),
                  (NodeType.ARGUMENT, []),
                  (NodeType.ARGUMENT, []),
                ]),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.ARGGROUP, [
                (NodeType.PARGGROUP, [
                  (NodeType.ARGUMENT, []),
                  (NodeType.ARGUMENT, []),
                ]),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
          ]),
          (NodeType.RPAREN, []),
        ]),
        (NodeType.WHITESPACE, []),
      ]),
    ]

    self.expect_format = """\
add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
                   COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
                                           ${CMAKE_CURRENT_BINARY_DIR}
                   COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
                   DEPENDS ${foobar_docs}
                   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
"""


if __name__ == '__main__':
  unittest.main()
