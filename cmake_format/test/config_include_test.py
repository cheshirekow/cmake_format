"""
Test the include mechanism for loading configs
"""

from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import shutil
import tempfile
import unittest

from cmake_format import __main__


class TestConfigInclude(unittest.TestCase):

  outdir = None

  def _list2reason(self, exc_list):
    if exc_list and exc_list[-1][0] is self:
      return exc_list[-1][1]
    return None

  def _test_passed(self):
    # Taken from https://stackoverflow.com/a/39606065/141023
    if hasattr(self, '_outcome'):  # Python 3.4+
      # these 2 methods have no side effects
      result = self.defaultTestResult()
      self._feedErrorsToResult(result, self._outcome.errors)
    else:  # Python 3.2 - 3.3 or 3.0 - 3.1 and 2.7
      result = getattr(
          self, '_outcomeForDoCleanups',
          self._resultForDoCleanups) # pylint: disable=no-member

    error = self._list2reason(result.errors)
    failure = self._list2reason(result.failures)
    return not error and not failure

    # # demo:   report short info immediately (not important)
    # if not ok:
    #   typ, text = ('ERROR', error) if error else ('FAIL', failure)
    #   msg = [x for x in text.split('\n')[1:] if not x.startswith(' ')][0]
    #   print("\n%s: %s\n     %s" % (typ, self.id(), msg))

  def setUp(self):
    self.outdir = tempfile.mkdtemp(
        prefix="cmake-format-{}-".format(self._testMethodName))

  def tearDown(self):
    if self._test_passed():
      shutil.rmtree(self.outdir)

  def test_single_include(self):
    outpath = os.path.join(self.outdir, "config-2.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
var_a = "hello"
      """)

    outpath = os.path.join(self.outdir, "config-1.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
include = ["config-2.py"]
var_b = "world"
      """)

    config_dict = __main__.get_configdict([outpath])
    self.assertIn("var_a", config_dict)
    self.assertIn("var_b", config_dict)

  def test_nested_include(self):
    outpath = os.path.join(self.outdir, "config-3.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
var_a = "hello"
      """)

    outpath = os.path.join(self.outdir, "config-2.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
include = ["config-3.py"]
var_b = "world"
      """)

    outpath = os.path.join(self.outdir, "config-1.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
include = ["config-2.py"]
var_c = "foobar"
      """)

    config_dict = __main__.get_configdict([outpath])
    self.assertIn("var_a", config_dict)
    self.assertIn("var_b", config_dict)
    self.assertIn("var_c", config_dict)

  def test_relative_path(self):
    subdir_path = os.path.join(self.outdir, "subdir")
    os.makedirs(subdir_path)
    outpath = os.path.join(subdir_path, "config-2.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
var_a = "hello"
      """)

    outpath = os.path.join(self.outdir, "config-1.py")
    with io.open(outpath, "w") as outfile:
      outfile.write("""
include = ["subdir/config-2.py"]
var_b = "world"
      """)

    config_dict = __main__.get_configdict([outpath])
    self.assertIn("var_a", config_dict)
    self.assertIn("var_b", config_dict)


if __name__ == "__main__":
  unittest.main()
