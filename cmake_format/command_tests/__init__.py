# -*- coding: utf-8 -*-
# pylint: disable=R1708
from __future__ import unicode_literals

import contextlib
import difflib
import functools
import inspect
import io
import os
import sys
import unittest

import re
import six

from cmake_format import __main__
from cmake_format import configuration
from cmake_format import formatter
from cmake_format import lexer
from cmake_format import parse
from cmake_format import parse_funs
from cmake_format.parse.common import NodeType
from cmake_format.parse.printer import test_string, tree_string


def strip_indent(content, indent=6):
  """
  Strings used in this file are indented by 6-spaces to keep them readable
  within the python code that they are embedded. Remove those 6-spaces from
  the front of each line before running the tests.
  """

  # NOTE(josh): don't use splitlines() so that we get the same result
  # regardless of windows or unix line endings in content.
  return '\n'.join([line[indent:] for line in content.split('\n')])


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


def replace_camel_to_snake(camel_pair):
  """
  Substituion callback for camel_to_snake
  """
  chars = camel_pair.group(0)
  return "{}_{}".format(chars[0], chars[1])


def camel_to_snake(camelstr):
  """
  Translate a camelCaseString into a snake_case_string
  """
  return re.sub("[a-z][A-Z]", replace_camel_to_snake, camelstr).lower()


def find_sidecar(filepath, cls):
  if filepath is not None:
    if filepath.endswith(".py"):
      return filepath[:-3] + ".cmake"
    return filepath

  thisdir = os.path.dirname(__file__)
  clsname = cls.__name__
  if clsname.startswith("Test"):
    clsname = clsname[4:]
  candidate = camel_to_snake(clsname) + ".cmake"
  candidate = os.path.join(thisdir, candidate)
  if os.path.exists(candidate):
    return candidate
  candidate = camel_to_snake(clsname) + "_tests.cmake"
  candidate = os.path.join(thisdir, candidate)
  if os.path.exists(candidate):
    return candidate
  candidate = inspect.getfile(cls)[:-3] + ".cmake"
  if os.path.exists(candidate):
    return candidate
  return None


def assert_lex(test, input_str, expected_types):
  """
  Run the lexer on the input string and assert that the result tokens match
  the expected
  """
  test.assertEqual(expected_types,
                   [tok.type for tok in lexer.tokenize(input_str)])


def assert_parse_tree(test, nodes, tups, tree=None, history=None):
  """
  Check the output tree structure against that of expect_tree: a nested tuple
  tree.
  """

  if tree is None:
    tree = nodes

  if history is None:
    history = []

  for node, tup in overzip(nodes, tups):
    if isinstance(node, lexer.Token):
      continue
    message = ("For node {} at\n {} within \n{}. "
               "If this is infact correct, copy-paste this:\n\n{}"
               .format(node, tree_string([node]),
                       tree_string(tree, history),
                       test_string(tree, ' ' * 6, ' ' * 2)))
    test.assertIsNotNone(node, msg="Missing node " + message)
    test.assertIsNotNone(tup, msg="Extra node " + message)
    expect_type, expect_children = tup
    test.assertEqual(node.node_type, expect_type,
                     msg="Expected type={} ".format(expect_type) + message)
    assert_parse_tree(test, node.children, expect_children, tree,
                      history + [node])


def assert_parse(test, input_str, expect_tree):
  """
  Run the parser to get the fst, then compare the result to the types in the
  ``expect_tree`` tuple tree.
  """
  tokens = lexer.tokenize(input_str)
  fst_root = parse.parse(tokens, test.parse_ctx)
  assert_parse_tree(test, [fst_root], expect_tree)


def assert_layout_tree(test, nodes, tups, tree=None, history=None):
  if tree is None:
    tree = nodes
  if history is None:
    history = []

  for node, tup in overzip(nodes, tups):
    if isinstance(node, lexer.Token):
      continue
    subhistory = history + [node]
    message = (" for node {} at\n {} \n\n\n"
               "If the actual result is expected, then update the test with"
               " this:\n{}"
               .format(node,
                       formatter.tree_string(tree, subhistory),
                       formatter.test_string(tree, ' ' * 6, ' ' * 2)))
    test.assertIsNotNone(node, msg="Missing node" + message)
    test.assertIsNotNone(tup, msg="Extra node" + message)
    if len(tup) == 6:
      ntype, wrap, row, col, colextent, expect_children = tup
      test.assertEqual(node.wrap, wrap,
                       msg="Expected wrap={}".format(wrap) + message)
    else:
      ntype, row, col, colextent, expect_children = tup

    test.assertEqual(node.type, ntype,
                     msg="Expected type={}".format(ntype) + message)
    test.assertEqual(node.position[0], row,
                     msg="Expected row={}".format(row) + message)
    test.assertEqual(node.position[1], col,
                     msg="Expected col={}".format(col) + message)
    test.assertEqual(node.colextent, colextent,
                     msg="Expected colextent={}".format(colextent) + message)
    assert_layout_tree(test, node.children, expect_children, tree, subhistory)


def assert_layout(test, input_str, expect_tree, strip_len=0):
  """
  Run the formatter on the input string and assert that the result matches
  the output string
  """

  input_str = strip_indent(input_str, strip_len)
  tokens = lexer.tokenize(input_str)
  parse_tree = parse.parse(tokens, test.parse_db)
  box_tree = formatter.layout_tree(parse_tree, test.config)
  assert_layout_tree(test, [box_tree], expect_tree)


def assert_format(test, input_str, output_str=None, strip_len=0):
  """
  Run the formatter on the input string and assert that the result matches
  the output string
  """
  if output_str is None:
    output_str = input_str

  input_str = strip_indent(input_str, strip_len)
  output_str = strip_indent(output_str, strip_len)

  if sys.version_info[0] < 3:
    assert isinstance(input_str, unicode)

  actual_str, _reflow_valid = __main__.process_file(test.config, input_str)
  delta_lines = list(difflib.unified_diff(output_str.split('\n'),
                                          actual_str.split('\n')))
  delta = '\n'.join(delta_lines[2:])

  if actual_str != output_str:
    message = ('Input text:\n-----------------\n{}\n'
               'Output text:\n-----------------\n{}\n'
               'Expected Output:\n-----------------\n{}\n'
               'Diff:\n-----------------\n{}'
               .format(input_str,
                       actual_str,
                       output_str,
                       delta))
    if sys.version_info[0] < 3:
      message = message.encode('utf-8')
    raise AssertionError(message)


def exec_sidecar(test, body, meta):
  """
  Assert a formatting and, optionally, a lex, parse, or layout tree.
  """
  expect_lex = meta.pop("expect_lex", None)
  if expect_lex is not None:
    with test.subTest(phase="lex"):
      assert_lex(test, body, expect_lex)
  expect_parse = meta.pop("expect_parse", None)
  if expect_parse is not None:
    with test.subTest(phase="parse"):
      assert_parse(test, body, expect_parse)
  expect_layout = meta.pop("expect_layout", None)
  if expect_layout is not None:
    with test.subTest(phase="layout"):
      assert_layout(test, body, expect_layout)

  test.config = configuration.Configuration(**meta)
  # TODO(josh): just move this into the configuration for the one test where
  # it's needed.
  test.config.fn_spec.add(
      'foo',
      flags=['BAR', 'BAZ'],
      kwargs={
          "HEADERS": '*',
          "SOURCES": '*',
          "DEPENDS": '*'
      })

  with test.subTest(phase="format"):
    assert_format(test, body, body)


class WrapTestWithRunFun(object):
  """
  Given a instance of a bound test-method from a TestCase, wrap that with
  a callable that first calls the method, and then calls `
  test.assertExpectations()`. Which is really just an opaque way of
  automatically calling `test.assertExpectations()` at the end of each test
  method.
  """

  def __init__(self, test_object, bound_method):
    self.test_object = test_object
    self.bound_method = bound_method

  def __call__(self):
    self.bound_method()
    self.test_object.assertExpectations()


def consume_bracket_contents(lineiter):
  """
  Consume the content of a multiline bracket comment
  """
  linebuf = []
  for _, line in lineiter:
    if line == "]=]":
      break
    linebuf.append(line)
  return "\n".join(linebuf)


class SidecarMeta(type):
  """
  Since the unittest framework inspects class members prior to calling
  ``setUpClass`` there does not appear to be any additional hooks that we
  can use to automatically load sidecars. We use a metaclass so that when the
  test fixture class object is instanciated (class is defined) we can load the
  sidecars. This way test methods are loaded before ``unittest`` inspects the
  class.
  """
  def __new__(mcs, name, bases, dct):
    subcls = type.__new__(mcs, name, bases, dct)
    if name not in ("MetaBase", "TestBase"):
      subcls.load_sidecar_tests()
    return subcls


def make_test_fun(test_name, test_body, test_meta):
  def test_fun(self):
    return exec_sidecar(self, test_body, test_meta)
  if sys.version_info < (3, 0, 0):
    # In python 2.7 test_name is a unicode object. We need to convert it to
    # a string.
    test_name = test_name.encode("utf-8")
  test_fun.__name__ = test_name
  test_fun.__doc__ = " ".join(test_name.split("_")[1:])
  return test_fun


class TestBase(six.with_metaclass(SidecarMeta, unittest.TestCase)):
  """
  Given a bunch of example usages of a particular command, ensure that they
  lex, parse, layout, and format the same as expected.
  """
  kNumSidecarTests = 0
  kExpectNumSidecarTests = 0

  @classmethod
  def append_sidecar_test(cls, test_name, line_buffer, meta_str):
    """
    Add a new test loaded from the cmake sidecar file
    """

    # strip extra newlines
    while line_buffer and not line_buffer[-1].strip():
      line_buffer.pop(-1)

    meta = {}
    if meta_str is not None:
      meta["NodeType"] = NodeType
      exec(meta_str, meta)  # pylint: disable=exec-used
      meta.pop("__builtins__")
      meta.pop("NodeType")

    body = "\n".join(line_buffer) + "\n"
    closure = make_test_fun(test_name, body, meta)
    setattr(cls, "test_" + test_name, closure)
    cls.kNumSidecarTests += 1

  @classmethod
  def load_sidecar_tests(cls, filepath=None):
    cmake_sidecar = find_sidecar(filepath, cls)
    if not cmake_sidecar or not os.path.exists(cmake_sidecar):
      return
    with io.open(cmake_sidecar, "r", encoding="utf-8") as infile:
      lines = infile.read().split("\n")

    test_name = None
    line_buffer = []
    meta_str = None
    lineiter = enumerate(lines)
    for lineno, line in lineiter:
      if line.startswith("# test: "):
        if line_buffer:
          cls.append_sidecar_test(test_name, line_buffer, meta_str)
        test_name = line[8:]
        line_buffer = []
        meta_str = None
      elif line == "#[=[" and test_name and not line_buffer:
        meta_str = consume_bracket_contents(lineiter)
      elif line.endswith("# end-test"):
        if test_name is None:
          raise ValueError(
              "Malformed sidecar {}:{}".format(cmake_sidecar, lineno))
        cls.append_sidecar_test(test_name, line_buffer, meta_str)
        test_name = None
        line_buffer = []
        meta_str = None
      else:
        line_buffer.append(line)

    if line_buffer:
      cls.append_sidecar_test(test_name, line_buffer, meta_str)

  def test_numsidecar(self):
    """
    Sanity check to makesure all sidecar tests are run.
    """
    self.assertEqual(self.kExpectNumSidecarTests, self.kNumSidecarTests)

  def __init__(self, *args, **kwargs):
    super(TestBase, self).__init__(*args, **kwargs)
    self.config = configuration.Configuration()
    parse_db = parse_funs.get_parse_db()
    self.parse_ctx = parse.ParseContext(parse_db)
    self.source_str = None
    self.expect_lex = None
    self.expect_parse = None
    self.expect_layout = None
    self.expect_format = None

    # NOTE(josh): hacky introspective way of automatically calling
    # assertExpectations() at the end of every test_XXX() function
    for name in dir(self):
      if not name.startswith("test_"):
        continue
      value = getattr(self, name)
      if callable(value):
        setattr(self, name, WrapTestWithRunFun(self, value))

  def setUp(self):
    self.config.fn_spec.add(
        'foo',
        flags=['BAR', 'BAZ'],
        kwargs={
            "HEADERS": '*',
            "SOURCES": '*',
            "DEPENDS": '*'
        })

    self.parse_ctx.parse_db.update(
        parse_funs.get_legacy_parse(self.config.fn_spec).kwargs)

  @contextlib.contextmanager
  def subTest(self, msg=None, **params):
    # pylint: disable=no-member
    if sys.version_info < (3, 4, 0):
      yield None
    else:
      yield super(TestBase, self).subTest(msg=msg, **params)

  def assertExpectations(self):
    # Empty source_str is shorthand for "assertInvariant"
    if self.source_str is None:
      self.source_str = self.expect_format

    if self.expect_lex is not None:
      with self.subTest(phase="lex"):  # pylint: disable=no-member
        assert_lex(self, self.source_str, self.expect_lex)
    if self.expect_parse is not None:
      with self.subTest(phase="parse"):  # pylint: disable=no-member
        assert_parse(self, self.source_str, self.expect_parse)
    if self.expect_layout is not None:
      with self.subTest(phase="layout"):  # pylint: disable=no-member
        assert_layout(self, self.source_str, self.expect_layout)
    if self.expect_format is not None:
      with self.subTest(phase="format"):  # pylint: disable=no-member
        assert_format(self, self.source_str, self.expect_format)


class TestAddCustomCommand(TestBase):
  """
  Test various examples of add_custom_command()
  """
  kExpectNumSidecarTests = 4


class TestConditional(TestBase):
  """
  Test various examples of commands that take conditional statements
  """
  kExpectNumSidecarTests = 5


class TestExport(TestBase):
  """
  Test various examples of export()
  """
  kExpectNumSidecarTests = 1


class TestExternalProject(TestBase):
  """
  Test various examples of ExternalProject_xxx()
  """
  kExpectNumSidecarTests = 5


class TestFile(TestBase):
  """
  Test various examples of the file command
  """
  kExpectNumSidecarTests = 10


class TestForeach(TestBase):
  """
  Test various examples of the foreach() function
  """
  kExpectNumSidecarTests = 5


class TestInstall(TestBase):
  """
  Test various examples of the install command
  """
  kExpectNumSidecarTests = 3


class TestSetTargetProperties(TestBase):
  """
  Test various examples of the install command
  """
  kExpectNumSidecarTests = 1


class TestSet(TestBase):
  """
  Test various examples of the set() function
  """
  kExpectNumSidecarTests = 8
