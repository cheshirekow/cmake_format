# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestInstallCommands(TestBase):
  """
  Test various examples of the install command
  """
  kExpectNumSidecarTests = 2


if __name__ == '__main__':
  unittest.main()
