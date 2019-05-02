# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase
from cmake_format.parser import NodeType


class TestInstallCommands(TestBase):
  """
  Test various examples of the install command
  """

  def test_install_targets(self):
    self.source_str = """\
install(TARGETS ${PROJECT_NAME}
        EXPORT ${CMAKE_PROJECT_NAME}Targets
        ARCHIVE DESTINATION lib COMPONENT install-app
        LIBRARY DESTINATION lib COMPONENT install-app
        RUNTIME DESTINATION bin COMPONENT install-app)
"""

    self.expect_parse = [
      (NodeType.BODY, [
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
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.ARGGROUP, [
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
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.ARGGROUP, [
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
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.ARGGROUP, [
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
            ]),
          ]),
          (NodeType.RPAREN, []),
        ]),
        (NodeType.WHITESPACE, []),
      ]),
    ]

    self.expect_format = """\
install(TARGETS ${PROJECT_NAME}
        EXPORT ${CMAKE_PROJECT_NAME}Targets
        ARCHIVE DESTINATION lib COMPONENT install-app
        LIBRARY DESTINATION lib COMPONENT install-app
        RUNTIME DESTINATION bin COMPONENT install-app)
"""

  def test_kwarg_match_consumes(self):
    self.source_str = """\
install(TARGETS myprog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT runtime)
"""
    self.expect_format = """\
install(TARGETS myprog
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT runtime)
"""


if __name__ == '__main__':
  unittest.main()
