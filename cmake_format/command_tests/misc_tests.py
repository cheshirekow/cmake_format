# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
# pylint: disable=too-many-lines
from __future__ import unicode_literals

import io
import os
import unittest

from cmake_format import configuration
from cmake_format.command_tests import assert_format, TestBase


class TestMiscFormatting(TestBase):
  """
  Ensure that various inputs format the way we want them to
  """
  kExpectNumSidecarTests = 82

  def test_config_hashruler_minlength(self):

    # make sure changing hashruler_min_length works correctly
    # self.config.enable_markup = False
    for min_width in {3, 5, 7, 9}:
      self.config.markup.hashruler_min_length = min_width

      # NOTE(josh): these tests use short rulers that wont be picked up by
      # the default pattern
      self.config.markup.ruler_pattern = (r'#{%d}#*' % (min_width - 1))

      just_shy = '#' * (min_width - 1)
      just_right = '#' * min_width
      longer = '#' * (min_width + 2)
      full_line = '#' * (self.config.format.line_width - 2)

      assert_format(self, """
# A comment: min_width={min_width}, just_shy
{just_shy}
""".format(min_width=min_width, just_shy=just_shy),
          """\
# A comment: min_width={min_width}, just_shy
#
""".format(min_width=min_width))

      assert_format(self, """
# A comment: min_width={min_width}, just_right
{just_right}
""".format(min_width=min_width, just_right=just_right),
          """\
# A comment: min_width={min_width}, just_right
# {full_line}
""".format(min_width=min_width, full_line=full_line))

      assert_format(self, """
# A comment: min_width={min_width}, longer
{longer}
""".format(min_width=min_width, longer=longer),
          """\
# A comment: min_width={min_width}, longer
# {full_line}
""".format(min_width=min_width, full_line=full_line))

  def test_windows_line_endings_input(self):
    self.source_str = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

    self.expect_format = """\
#[[*********************************************
* Information line 1
* Information line 2
************************************************]]
"""

  def test_windows_line_endings_output(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'windows'
    self.config = configuration.Configuration(**config_dict)

    self.source_str = """\
#[[*********************************************
* Information line 1
* Information line 2
************************************************]]"""

    self.expect_format = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

  def test_auto_line_endings(self):
    config_dict = self.config.as_dict()
    config_dict['line_ending'] = 'auto'
    self.config = configuration.Configuration(**config_dict)

    self.source_str = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

    self.expect_format = (
        "#[[*********************************************\r\n"
        "* Information line 1\r\n"
        "* Information line 2\r\n"
        "************************************************]]\r\n")

  def test_byte_order_mark(self):
    self.source_str = """\
\ufeffcmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""
    self.expect_format = """\
cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

    self.config.encode.emit_byteorder_mark = True
    self.source_str = """\
cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""
    self.expect_format = """\
\ufeffcmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)
"""

  def test_example_file(self):
    thisdir = os.path.dirname(__file__)
    infile_path = os.path.join(thisdir, '..', 'test', 'test_in.cmake')
    outfile_path = os.path.join(thisdir, '..', 'test', 'test_out.cmake')

    with io.open(infile_path, 'r', encoding='utf8') as infile:
      infile_text = infile.read()
    with io.open(outfile_path, 'r', encoding='utf8') as outfile:
      outfile_text = outfile.read()

    self.source_str = infile_text
    self.expect_format = outfile_text


if __name__ == '__main__':
  unittest.main()
