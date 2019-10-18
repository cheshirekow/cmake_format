# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestSetCommand(TestBase):
  """
  Test various examples of the set() function
  """
  kExpectNumSidecarTests = 8


if __name__ == '__main__':
  unittest.main()
