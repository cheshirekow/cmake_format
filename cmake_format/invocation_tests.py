import difflib
import io
import os
import shutil
import subprocess
import sys
import unittest
import tempfile


class TestInvocations(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(TestInvocations, self).__init__(*args, **kwargs)
    self.tempdir = None

  def setUp(self):
    self.tempdir = tempfile.mkdtemp(prefix='cmakeformattest_')

  def tearDown(self):
    shutil.rmtree(self.tempdir)

  def test_default_invocation(self):
    thisdir = os.path.realpath(os.path.dirname(__file__))
    infile_path = os.path.join(thisdir, 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, 'test', 'test_out.cmake')

    with io.open(os.path.join(self.tempdir, 'test_out.cmake'), 'w',
                 encoding='utf8') as outfile:
      subprocess.check_call([sys.executable, '-Bm', 'cmake_format',
                             infile_path], cwd=self.tempdir, stdout=outfile)

    with io.open(os.path.join(self.tempdir, 'test_out.cmake'), 'r',
                 encoding='utf8') as infile:
      actual_text = infile.read()
    with io.open(outfile_path, 'r', encoding='utf8') as infile:
      expected_text = infile.read()

    delta_lines = list(difflib.unified_diff(actual_text.split('\n'),
                                            expected_text.split('\n')))
    if delta_lines:
      raise AssertionError('\n'.join(delta_lines[2:]))

  def test_fileout_invocation(self):
    thisdir = os.path.realpath(os.path.dirname(__file__))
    infile_path = os.path.join(thisdir, 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, 'test', 'test_out.cmake')

    subprocess.check_call([sys.executable, '-Bm', 'cmake_format',
                           '-o', os.path.join(self.tempdir, 'test_out.cmake'),
                           infile_path], cwd=self.tempdir)

    with io.open(os.path.join(self.tempdir, 'test_out.cmake'), 'r',
                 encoding='utf8') as infile:
      actual_text = infile.read()
    with io.open(outfile_path, 'r', encoding='utf8') as infile:
      expected_text = infile.read()

    delta_lines = list(difflib.unified_diff(actual_text.split('\n'),
                                            expected_text.split('\n')))
    if delta_lines:
      raise AssertionError('\n'.join(delta_lines[2:]))


if __name__ == '__main__':
  unittest.main()
