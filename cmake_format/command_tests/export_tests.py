# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestExportCommand(TestBase):
  """
  Test various examples of export()
  """

  def test_empty_parg_group(self):
    self.expect_format = """\
export(TARGETS FILE ${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}Targets.cmake)
"""


if __name__ == '__main__':
  unittest.main()
