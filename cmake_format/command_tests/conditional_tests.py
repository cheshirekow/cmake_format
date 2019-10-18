# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestConditionalCommands(TestBase):
  """
  Test various examples of commands that take conditional statements
  """
  kExpectNumSidecarTests = 5


if __name__ == '__main__':
  unittest.main()
