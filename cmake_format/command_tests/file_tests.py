# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestFileCommands(TestBase):
  """
  Test various examples of the file command
  """
  kExpectNumSidecarTests = 10


if __name__ == '__main__':
  unittest.main()
