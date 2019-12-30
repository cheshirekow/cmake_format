"""
Ensure that changes to cmake-format don't screw current users
"""

# -*- coding: utf-8 -*-
# pylint: disable=R1708
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import shutil
import sys
import subprocess
import tempfile
import unittest


def iter_filelist(rootdir, include_patterns, exclude_patterns):
  """
  Walk a directory tree and yield each file matching the include patterns
  but not matching the exclude patterns.
  """
  include_patterns = [re.compile(pattern) for pattern in include_patterns]
  exclude_patterns = [re.compile(pattern) for pattern in exclude_patterns]

  for cwd, dirnames, filenames in os.walk(rootdir):
    relpath_cwd = os.path.relpath(cwd, rootdir)
    if relpath_cwd == ".":
      relpath_cwd = ""

    exclude_cwd = any(pattern.match(relpath_cwd)
                      for pattern in exclude_patterns)
    if exclude_cwd:
      dirnames[:] = []
      continue

    dirnames[:] = sorted(dirnames)
    for filename in filenames:
      relpath_filename = os.path.join(relpath_cwd, filename)
      include_filename = (
          any(pattern.match(filename) for pattern in include_patterns) or
          any(pattern.match(relpath_filename) for pattern in include_patterns)
      )
      exclude_filename = (
          any(pattern.match(filename) for pattern in exclude_patterns) or
          any(pattern.match(relpath_filename) for pattern in exclude_patterns)
      )

      if include_filename and not exclude_filename:
        yield relpath_filename


class WrapTestWithRunFun(object):
  """
  Given a instance of a bound test-method from a TestCase, wrap that with
  a callable that first calls the method, and then calls `
  test.assertCanFormat()`. Which is really just an opaque way of
  automatically calling `rest.assertCanFormat()` at the end of each test
  method.
  """

  def __init__(self, test_object, bound_method):
    self.test_object = test_object
    self.bound_method = bound_method

  def __call__(self):
    self.bound_method()
    self.test_object.assertCanFormat()


class DontScrewUsers(unittest.TestCase):
  """
  Given a bunch of public repositories, check that cmake-format runs on
  all of them.
  """

  TMPDIR = None

  def __init__(self, *args, **kwargs):
    super(DontScrewUsers, self).__init__(*args, **kwargs)
    self.repository = None
    self.clonedir = None
    self.configpath = None
    self.include_patterns = [r".*\.cmake$", "CMakeLists.txt"]
    self.exclude_patterns = [r"\.git", r"\.build", r".*third_party.*"]
    self.last_known_good = None

    # NOTE(josh): hacky introspective way of automatically calling
    # assertExpectations() at the end of every test_XXX() function
    for name in dir(self):
      if not name.startswith("test_"):
        continue
      value = getattr(self, name)
      if callable(value):
        setattr(self, name, WrapTestWithRunFun(self, value))

  @classmethod
  def setUpClass(cls):
    if os.environ.get("CMFSCREWTEST_REUSE"):
      cls.TMPDIR = os.path.join(tempfile.gettempdir(), "cmf-unscrew")
      if not os.path.exists(cls.TMPDIR):
        os.makedirs(cls.TMPDIR)
    else:
      cls.TMPDIR = tempfile.mkdtemp(prefix="cmf-unscrew_")

  @classmethod
  def tearDownClass(cls):
    if not os.environ.get("CMFSCREWTEST_REUSE"):
      shutil.rmtree(cls.TMPDIR)

  def assertCanFormat(self):
    if self.clonedir is None:
      self.clonedir = self.repository.rsplit("/", 1)[1]
    clonepath = os.path.join(self.TMPDIR, self.clonedir)
    if not os.path.exists(os.path.join(clonepath, ".git")):
      subprocess.check_call(["git", "clone", "--depth", "1",
                             self.repository, self.clonedir], cwd=self.TMPDIR)

    env = os.environ.copy()
    thisdir = os.path.dirname(__file__)
    thisdir = os.path.dirname(thisdir)
    repodir = os.path.dirname(thisdir)
    env["PYTHONPATH"] = os.path.realpath(repodir)

    fmtcmd = [sys.executable, "-Bm", "cmake_format"]
    if self.configpath:
      fmtcmd += ["--config", self.configpath]
    fmtcmd += ["-i"]

    pathiter = iter_filelist(
        clonepath,
        self.include_patterns,
        self.exclude_patterns)

    nsuccess = 0
    failed_files = []
    for relpath in pathiter:
      result = subprocess.call(fmtcmd + [relpath], cwd=clonepath, env=env)
      if result == 0:
        nsuccess += 1
      else:
        failed_files.append(relpath)

    print("{}: Successfully ran on {} files".format(self.clonedir, nsuccess))
    if failed_files:
      print("  " + "\n  ".join(failed_files))

    self.assertFalse(failed_files)

  def test_thisrepo(self):
    thisdir = os.path.realpath(os.path.dirname(__file__))
    self.repository = os.sep.join(thisdir.split(os.sep)[:-2])
    self.configpath = ".cmake-format.py"
    self.last_known_good = "efb0d6256fcbc4a3cfad9f5ebdaa34172d230ea2"
    self.exclude_patterns += [
        r"test_latin.*\.cmake"
    ]

  def test_elektra(self):
    self.repository = "https://github.com/sanssecours/elektra"
    self.configpath = ".cmake-format.yaml"
    self.last_known_good = "483752d182bc12546a2902989d63ea1cfcaae861"

  def test_pcl(self):
    self.repository = "https://github.com/PointCloudLibrary/pcl"
    self.last_known_good = "711b12144e2cb250fcbccf56b0c523a1d279297a"

  def test_arrow(self):
    self.repository = "https://github.com/apache/arrow"
    self.configpath = "cmake-format.py"
    self.last_known_good = "e32c0b3279df76d68c93724f476dfcf0c1c44fa5"
    self.exclude_patterns += [
        r".*\.h\.cmake",
        r".*Dockerfile\.cmake",
    ]

  def test_aom(self):
    self.repository = "https://aomedia.googlesource.com/aom"
    self.configpath = ".cmake-format.py"
    self.last_known_good = "81259cf147effcd93fc50fca768ade453fce0bfe"

  def test_vulkan_tools(self):
    self.repository = "https://github.com/KhronosGroup/Vulkan-Tools"
    self.configpath = ".cmake-format.py"
    self.last_known_good = "4c6673b2973a7434716a9325a0b22861beed9244"

  def test_vulkan_validation_layers(self):
    self.repository = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    self.configpath = "scripts/cmake-format.py"
    self.last_known_good = "adbfa85caafb5f240474dd2ae2414f0b78026a3f"
    self.exclude_patterns += [
        ".*build-android/cmake/layerlib/CMakeLists.txt"
    ]

  def test_vulkan_validation_loader(self):
    self.repository = "https://github.com/KhronosGroup/Vulkan-Loader"
    self.configpath = ".cmake-format.py"

  def test_pdfslicer(self):
    self.repository = "https://github.com/junrrein/pdfslicer"
    self.configpath = ".cmake-format.py"

  def test_opencensus(self):
    self.repository = "https://github.com/census-instrumentation/opencensus-cpp"
    self.configpath = ".cmake-format.py"

  def test_openbmc_ipmbbridge(self):
    self.repository = "https://github.com/openbmc/ipmbbridge"
    self.configpath = "cmake-format.json"

  def test_openbmc_dbus_sensors(self):
    self.repository = "https://github.com/openbmc/dbus-sensors"
    self.configpath = "cmake-format.json"


if __name__ == "__main__":
  unittest.main()
