# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestAddExecutableCommand(TestBase):
  """
  Test various examples of add_executable()
  """
  kExpectNumSidecarTests = 6

  def test_sort_arguments(self):
    self.config.autosort = True
    self.source_str = """\
add_executable(foobar WIN32 sourcefile_04.cc sourcefile_02.cc sourcefile_03.cc
                            sourcefile_01.cc)
"""
    self.expect_format = """\
add_executable(foobar WIN32 sourcefile_01.cc sourcefile_02.cc sourcefile_03.cc
                            sourcefile_04.cc)
"""


if __name__ == '__main__':
  unittest.main()
