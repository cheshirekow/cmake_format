# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestAddCustomCommand(TestBase):
  """
  Test various examples of add_custom_command()
  """
  kExpectNumSidecarTests = 1


if __name__ == '__main__':
  unittest.main()
