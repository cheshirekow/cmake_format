import os
import unittest
import subprocess
import sys


class TestDocSources(unittest.TestCase):
  """
  Ensure that dynamic documentation content is up-to-date
  """

  def test_docsources_uptodate(self):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    with open("/dev/null", "w") as devnull:
      result = subprocess.call(
          [sys.executable, "-B", "gendoc_sources.py", "--verify"],
          cwd=thisdir, stderr=devnull)
    self.assertEqual(0, result)


if __name__ == '__main__':
  unittest.main()
