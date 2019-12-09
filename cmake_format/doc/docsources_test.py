import os
import unittest
import subprocess
import sys
import tempfile


class TestDocSources(unittest.TestCase):
  """
  Ensure that dynamic documentation content is up-to-date
  """

  def test_docsources_uptodate(self):
    rootdir = os.path.realpath(__file__)
    for _ in range(3):
      rootdir = os.path.dirname(rootdir)

    with tempfile.NamedTemporaryFile(delete=False) as errlog:
      errlogpath = errlog.name
      result = subprocess.call(
          [sys.executable, "-Bm", "cmake_format.doc.gendoc_sources",
           "--verify"],
          cwd=rootdir, stderr=errlog)
    with open(errlogpath, "r") as infile:
      errmsg = "Error log: \n" + infile.read()
    os.unlink(errlogpath)
    self.assertEqual(0, result, errmsg)


if __name__ == '__main__':
  unittest.main()
