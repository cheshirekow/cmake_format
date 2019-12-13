# -*- coding: utf-8 -*-
# pylint: disable=R1708
from __future__ import unicode_literals

import io
import logging
import os
import re
import sys
import unittest

from cmake_format import configuration
from cmake_format import lexer

from cmake_lint import __main__
from cmake_lint import lint_util
from cmake_lint.test import genfiles


def overzip(iterable_a, iterable_b):
  """
  Like itertools.izip but instead if the two lists have different sizes then
  the resulting generator will yield a number of pairs equal to the larger of
  the two inputs (rathe than the smaller). The empty list will be padded with
  None elements.
  """
  iter_a = iter(iterable_a)
  iter_b = iter(iterable_b)

  item_a = next(iter_a, None)
  item_b = next(iter_b, None)

  # NOTE(josh): this only matters when overzipping a parse tree. It's not
  # meaningful for overzipping a layout tree, but it doesn't hurt since
  # lexer tokens don't show up in the layout tree
  while isinstance(item_a, lexer.Token):
    item_a = next(iter_a, None)

  while item_a is not None and item_b is not None:
    yield(item_a, item_b)
    item_a = next(iter_a, None)
    while isinstance(item_a, lexer.Token):
      item_a = next(iter_a, None)
    item_b = next(iter_b, None)

  while item_a is not None:
    yield(item_a, None)
    item_a = next(iter_a, None)
    while isinstance(item_a, lexer.Token):
      item_a = next(iter_a, None)

  while item_b is not None:
    yield(None, item_b)
    item_b = next(iter_b, None)


def camel_to_snake_callback(match):
  """
  Substituion callback for camel_to_snake
  """
  chars = match.group(0)
  return "{}_{}".format(chars[0], chars[1])


def camel_to_snake(camelstr):
  """
  Translate a camelCaseString into a snake_case_string
  """
  return re.sub("[a-z][A-Z]", camel_to_snake_callback, camelstr).lower()


def snake_to_camel_callback(match):
  """
  Substituion callback for camel_to_snake
  """
  snake_chars = match.group(0)
  return snake_chars[0] + snake_chars[-1].upper()


def snake_to_camel(camelstr, upper=False):
  """
  Translate a camelCaseString into a snake_case_string
  """
  lower_camel = re.sub("([^_]?_+[^_]?)", snake_to_camel_callback, camelstr)
  if upper:
    return lower_camel[0].upper() + lower_camel[1:]
  return lower_camel


class TestBase(unittest.TestCase):
  def execute_test(self, test_name, test_body, expect_list):
    outfile = io.StringIO()
    global_ctx = lint_util.GlobalContext(outfile)
    local_ctx = global_ctx.get_file_ctx(test_name)
    config = configuration.Configuration()
    __main__.process_file(config, local_ctx, test_body)
    for actual, expected in overzip(local_ctx.get_lint(), expect_list):
      if expected is None:
        raise AssertionError(
            "More lint than expected, starting with {}".format(actual))

      if "@" in expected:
        expect_id, expect_locstr = expected.split("@")
        expect_loc = tuple(int(val) for val in expect_locstr.split(":"))
      else:
        expect_id = expected
        expect_loc = ()

      if actual is None:
        if expect_loc:
          raise AssertionError(
              "Missing expected lint {} at {}".format(expect_id, expect_loc))
        else:
          raise AssertionError(
              "Missing expected lint {}".format(expect_id))

      if expect_id != actual.spec.idstr:
        raise AssertionError(
            "Expected lint {} but got lint {}".format(expect_id, actual))

      actual_loc = actual.location
      if actual_loc is None:
        actual_loc = ()
      for expect_val, actual_val in zip(expect_loc, actual_loc):
        if expect_val != actual_val:
          raise AssertionError(
              "Expected lint {}@{} but got it at {}".format(
                  expect_id, ":".join(str(x) for x in expect_loc),
                  actual_loc))


def iter_testfiles():
  thisdir = os.path.dirname(os.path.realpath(__file__))
  for dirpath, _dirnames, filenames in os.walk(thisdir):
    for filename in filenames:
      if filename.endswith(".cmake"):
        yield os.path.join(dirpath, filename)


def iter_tests_from_file(filepath):
  with io.open(filepath, "r", newline='') as infile:
    # Split lines but if the final newline is missing then preserve that fact
    items = re.split("(\n)", infile.read())
    lines = []
    for item in items:
      if item == "\n":
        lines[-1] += item
      else:
        lines.append(item)

  # Simple state-machine parser
  test_name = None
  line_buffer = []
  expect_str = None
  lineiter = enumerate(lines)
  for lineno, line in lineiter:
    if line.startswith("# test: "):
      if line_buffer:
        if test_name is None:
          raise ValueError(
              "Malformed sidecar {}:{}".format(filepath, lineno))
        yield (test_name, "".join(line_buffer), expect_str)
      test_name = line[len("# test: "):].rstrip()
      line_buffer = []
      expect_str = None
    elif line.startswith("# expect: "):
      expect_str = line[len("# expect: "):]
    elif line.endswith("# end-test"):
      if test_name is None:
        raise ValueError(
            "Malformed sidecar {}:{}".format(filepath, lineno))
      yield (test_name, "".join(line_buffer), expect_str)
      test_name = None
      line_buffer = []
      expect_str = None
    else:
      line_buffer.append(line)

  if test_name and line_buffer:
    yield (test_name, "".join(line_buffer), expect_str)


def make_test_fun(test_name, test_body, expect_list):
  def test_fun(self):
    self.execute_test(test_name, test_body, expect_list)
  if sys.version_info < (3, 0, 0):
    # In python 2.7 test_name is a unicode object. We need to convert it to
    # a string.
    test_name = test_name.encode("utf-8")
  test_fun.__name__ = test_name
  return test_fun


def gen_test_classes():
  for filepath in iter_testfiles():
    basename = os.path.splitext(os.path.basename(filepath))[0]
    classname = snake_to_camel(basename, upper=True)
    defn = {}
    for test_name, test_body, expect_str in iter_tests_from_file(filepath):
      method_name = "test_" + test_name.replace("-", "_")
      expect_list = expect_str.rstrip().split(",")
      defn[method_name] = make_test_fun(method_name, test_body, expect_list)

    yield type(classname, (TestBase,), defn)


if __name__ == "__main__":
  genfiles.rewrite_lint_tests()

classobj = None
for classobj in gen_test_classes():
  globals()[classobj.__name__] = classobj
del classobj

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  unittest.main()
