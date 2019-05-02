# -*- coding: utf-8 -*-
# pylint: disable=R1708
from __future__ import unicode_literals

import difflib
import io
import sys
import unittest

from cmake_format import __main__
from cmake_format import configuration
from cmake_format import formatter
from cmake_format import lexer
from cmake_format import parser
from cmake_format import parse_funs
from cmake_format.parser import NodeType


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
               .format(node, parser.tree_string([node]),
                       parser.tree_string(tree, history),
                       parser.test_string(tree, ' ' * 6, ' ' * 2)))
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

  fst_root = parser.parse(tokens, test.parse_db)
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


def assert_layout(test, input_str, expect_tree, strip_len=6):
  """
  Run the formatter on the input string and assert that the result matches
  the output string
  """

  input_str = strip_indent(input_str, strip_len)
  tokens = lexer.tokenize(input_str)
  parse_tree = parser.parse(tokens, test.parse_db)
  box_tree = formatter.layout_tree(parse_tree, test.config)
  assert_layout_tree(test, [box_tree], expect_tree)


def assert_format(test, input_str, output_str, strip_len=0):
  """
  Run the formatter on the input string and assert that the result matches
  the output string
  """

  input_str = strip_indent(input_str, strip_len)
  output_str = strip_indent(output_str, strip_len)

  if sys.version_info[0] < 3:
    assert isinstance(input_str, unicode)
  infile = io.StringIO(input_str)
  outfile = io.StringIO()

  __main__.process_file(test.config, infile, outfile)
  delta_lines = list(difflib.unified_diff(output_str.split('\n'),
                                          outfile.getvalue().split('\n')))
  delta = '\n'.join(delta_lines[2:])

  if outfile.getvalue() != output_str:
    message = ('Input text:\n-----------------\n{}\n'
               'Output text:\n-----------------\n{}\n'
               'Expected Output:\n-----------------\n{}\n'
               'Diff:\n-----------------\n{}'
               .format(input_str,
                       outfile.getvalue(),
                       output_str,
                       delta))
    if sys.version_info[0] < 3:
      message = message.encode('utf-8')
    raise AssertionError(message)


class WrapTestWithRunFun(object):
  """
  Given a instance of a bound test-method from a TestCase, wrap that with
  a callable that first calls the method, and then calls `
  test.assertExpectations()`. Which is really just an opaque way of
  automatically calling `rest.assertExpectations()` at the end of each test
  method.
  """

  def __init__(self, test_object, bound_method):
    self.test_object = test_object
    self.bound_method = bound_method

  def __call__(self):
    self.bound_method()
    self.test_object.assertExpectations()


class TestBase(unittest.TestCase):
  """
  Given a bunch of example usages of a particular command, ensure that they
  lex, parse, layout, and format the same as expected.
  """

  def __init__(self, *args, **kwargs):
    super(TestBase, self).__init__(*args, **kwargs)
    self.config = configuration.Configuration()
    self.parse_db = parse_funs.get_parse_db()
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

    self.parse_db.update(
        parse_funs.get_legacy_parse(self.config.fn_spec).kwargs)

    for name, value in vars(self).items():
      if callable(value) and name.startswith("test_"):
        setattr(self, name, WrapTestWithRunFun(self, value))

  def assertExpectations(self):
    # Empty source_str is shorthand for "assertInvariant"
    if self.source_str is None:
      self.source_str = self.expect_format

    if sys.version_info < (3, 0, 0):
      if self.expect_lex is not None:
        assert_lex(self, self.source_str, self.expect_lex)
      if self.expect_parse is not None:
        assert_parse(self, self.source_str, self.expect_parse)
      if self.expect_layout is not None:
        assert_layout(self, self.source_str, self.expect_layout)
      if self.expect_format is not None:
        assert_format(self, self.source_str, self.expect_format)
    else:
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
