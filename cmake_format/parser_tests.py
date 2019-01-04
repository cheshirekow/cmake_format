# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from cmake_format import configuration
from cmake_format import lexer
from cmake_format import parser
from cmake_format.parser import NodeType


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


def assert_tree_type(test, nodes, tups, tree=None):
  """
  Check the output tree structure against that of expect_tree: a nested tuple
  tree.
  """

  if tree is None:
    tree = nodes

  for node, tup in overzip(nodes, tups):
    if isinstance(node, lexer.Token):
      continue
    message = ("For node {} at\n {} within \n{}. "
               "If this is infact correct, copy-paste this:\n\n{}"
               .format(node, parser.tree_string([node]),
                       parser.tree_string(tree),
                       parser.test_string(tree)))
    test.assertIsNotNone(node, msg="Missing node" + message)
    test.assertIsNotNone(tup, msg="Extra node" + message)
    expect_type, expect_children = tup
    test.assertEqual(node.node_type, expect_type,
                     msg="Expected type={} ".format(expect_type) + message)
    assert_tree_type(test, node.children, expect_children, tree)


class TestCanonicalParse(unittest.TestCase):
  """
  Given a bunch of example inputs, ensure that they parse into the expected
  tree structure.
  """

  def __init__(self, *args, **kwargs):
    super(TestCanonicalParse, self).__init__(*args, **kwargs)
    self.config = configuration.Configuration()

  def setUp(self):
    self.config.fn_spec.add(
        'foo',
        flags=['BAR', 'BAZ'],
        kwargs={
            "HEADERS": '*',
            "SOURCES": '*',
            "DEPENDS": '*'
        })

  def do_type_test(self, input_str, expect_tree):
    """
    Run the parser to get the fst, then compare the result to the types in the
    ``expect_tree`` tuple tree.
    """
    tokens = lexer.tokenize(input_str)
    fst_root = parser.parse(tokens, self.config.fn_spec)
    assert_tree_type(self, [fst_root], expect_tree)

  def test_collapse_additional_newlines(self):
    self.do_type_test("""\
      # The following multiple newlines should be collapsed into a single newline




      cmake_minimum_required(VERSION 2.8.11)
      project(cmake_format_test)
      """, [
          (NodeType.BODY, [
              (NodeType.WHITESPACE, []),
              (NodeType.COMMENT, []),
              (NodeType.WHITESPACE, []),
              (NodeType.STATEMENT, [
                  (NodeType.FUNNAME, []),
                  (NodeType.LPAREN, []),
                  (NodeType.ARGGROUP, [
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                  ]),
                  (NodeType.RPAREN, []),
              ]),
              (NodeType.WHITESPACE, []),
              (NodeType.STATEMENT, [
                  (NodeType.FUNNAME, []),
                  (NodeType.LPAREN, []),
                  (NodeType.ARGGROUP, [
                      (NodeType.ARGUMENT, []),
                  ]),
                  (NodeType.RPAREN, []),
              ]),
              (NodeType.WHITESPACE, []),
          ]),
      ])

  def test_multiline_comment(self):
    self.do_type_test("""\
      # This multiline-comment should be reflowed
      # into a single comment
      # on one line
      """, [
          (NodeType.BODY, [
              (NodeType.WHITESPACE, []),
              (NodeType.COMMENT, []),
              (NodeType.WHITESPACE, []),
          ])
      ])

  def test_nested_kwargs(self):
    self.do_type_test("""\
      add_custom_target(ALL VERBATIM
        COMMAND echo hello world
        COMMENT this is some text)
      """, [
          (NodeType.BODY, [
              (NodeType.WHITESPACE, []),
              (NodeType.STATEMENT, [
                  (NodeType.FUNNAME, []),
                  (NodeType.LPAREN, []),
                  (NodeType.ARGGROUP, [
                      (NodeType.FLAG, []),
                      (NodeType.FLAG, []),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                  ]),
                  (NodeType.RPAREN, []),
              ]),
              (NodeType.WHITESPACE, []),
          ]),
      ])

  def test_custom_command(self):
    self.do_type_test("""\
      # This very long command should be broken up along keyword arguments
      foo(nonkwarg_a nonkwarg_b HEADERS a.h b.h c.h d.h e.h f.h SOURCES a.cc b.cc d.cc DEPENDS foo bar baz)
      """, [
          (NodeType.BODY, [
              (NodeType.WHITESPACE, []),
              (NodeType.COMMENT, []),
              (NodeType.WHITESPACE, []),
              (NodeType.STATEMENT, [
                  (NodeType.FUNNAME, []),
                  (NodeType.LPAREN, []),
                  (NodeType.ARGGROUP, [
                      (NodeType.ARGUMENT, []),
                      (NodeType.ARGUMENT, []),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                      (NodeType.FLAG, []),
                      (NodeType.FLAG, []),
                  ]),
                  (NodeType.RPAREN, []),
              ]),
              (NodeType.WHITESPACE, []),
          ]),
      ])

  def test_shellcommand_parse(self):
    self.do_type_test("""\
      add_test(NAME foo-test
               COMMAND command -Bm -h --hello foo bar --world baz buck
               WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
      """, [
          (NodeType.BODY, [
              (NodeType.WHITESPACE, []),
              (NodeType.STATEMENT, [
                  (NodeType.FUNNAME, []),
                  (NodeType.LPAREN, []),
                  (NodeType.ARGGROUP, [
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.FLAG, []),
                          (NodeType.FLAG, []),
                          (NodeType.KWARGGROUP, [
                              (NodeType.KEYWORD, []),
                              (NodeType.ARGUMENT, []),
                              (NodeType.ARGUMENT, []),
                          ]),
                          (NodeType.KWARGGROUP, [
                              (NodeType.KEYWORD, []),
                              (NodeType.ARGUMENT, []),
                              (NodeType.ARGUMENT, []),
                          ]),
                      ]),
                      (NodeType.KWARGGROUP, [
                          (NodeType.KEYWORD, []),
                          (NodeType.ARGUMENT, []),
                      ]),
                  ]),
                  (NodeType.RPAREN, []),
              ]),
              (NodeType.WHITESPACE, []),
          ]),
      ])


if __name__ == '__main__':
  unittest.main()
