# pylint: disable=bad-continuation
from __future__ import unicode_literals
import unittest

from cmake_format.command_tests import TestBase


class TestConditionalCommands(TestBase):
  """
  Test various examples of commands that take conditional statements
  """

  def test_complicated_boolean(self):
    self.config.max_subargs_per_line = 10
    self.expect_format = """\
set(matchme "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
   OR (CONFIG_AV1_ENCODER
       AND CONFIG_ENCODE_PERF_TESTS
       AND "${var}" MATCHES "_ENCODE_PERF_TEST_")
   OR (CONFIG_AV1_DECODER
       AND CONFIG_DECODE_PERF_TESTS
       AND "${var}" MATCHES "_DECODE_PERF_TEST_")
   OR (CONFIG_AV1_ENCODER AND "${var}" MATCHES "_TEST_ENCODER_")
   OR (CONFIG_AV1_DECODER AND "${var}" MATCHES "_TEST_DECODER_"))
  list(APPEND aom_test_source_vars ${var})
endif()
"""

  def test_nested_parens(self):
    self.expect_format = """\
if((NOT HELLO) OR (NOT EXISTS ${WORLD}))
  message(WARNING "something is wrong")
  set(foobar FALSE)
endif()
"""

  def test_negated_single_nested_parens(self):
    self.expect_format = """\
if(NOT ("" STREQUALS ""))
  # pass
endif()
"""

  def test_conditional_in_if_and_endif(self):
    self.expect_format = """\
if(SOMETHING AND (NOT SOMETHING_ELSE STREQUAL ""))
  # pass
endif(SOMETHING AND (NOT SOMETHING_ELSE STREQUAL ""))
"""


if __name__ == '__main__':
  unittest.main()
