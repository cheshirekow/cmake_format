import os
import subprocess
import sys
import tempfile
import unittest

ROOTDIR = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-3])


def iter_testfiles():
  testsdir = os.path.join(ROOTDIR, "cmake_format", "command_tests")
  for filename in os.listdir(testsdir):
    if filename.endswith("_tests.cmake"):
      yield os.path.join("cmake_format", "command_tests", filename)


def make_test_fun(testname, filepath):
  def test_fun(testcase):
    with tempfile.NamedTemporaryFile(mode="wb") as outfile:
      result = subprocess.call(
          [sys.executable, "-Bm", "cmake_lint", filepath],
          cwd=ROOTDIR, stdout=outfile)
    testcase.assertNotEqual(2, result)

  if sys.version_info < (3, 0, 0):
    # In python 2.7 test_name is a unicode object. We need to convert it to
    # a string.
    testname = testname.encode("utf-8")
  test_fun.__name__ = testname
  test_fun.__doc__ = " ".join(testname.split("_")[1:])
  return test_fun


def gen_test_class():
  defn = {}
  for filepath in iter_testfiles():
    basename = filepath.split(os.sep)[-1][:-len("_tests.cmake")]
    testname = "test_" + basename
    defn[testname] = make_test_fun(testname, filepath)
  return type("TestFormatFiles", (unittest.TestCase,), defn)


TestFormatFiles = gen_test_class()

if __name__ == "__main__":
  sys.exit(unittest.main())
