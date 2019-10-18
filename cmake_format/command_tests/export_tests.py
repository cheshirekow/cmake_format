# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestExportCommand(TestBase):
  """
  Test various examples of export()
  """
  kExpectNumSidecarTests = 1


if __name__ == '__main__':
  unittest.main()
