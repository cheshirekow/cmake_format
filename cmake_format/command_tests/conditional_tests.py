# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestConditionalCommands(TestBase):
  """
  Test various examples of commands that take conditional statements
  """
  kNumSidecarTests = 0

  def test_numsidecar(self):
    """
    Sanity check to makesure all sidecar tests are run.
    """
    self.assertEqual(5, self.kNumSidecarTests)


TestConditionalCommands.load_sidecar_tests()

if __name__ == '__main__':
  unittest.main()
