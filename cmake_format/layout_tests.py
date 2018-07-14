# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import unittest

from cmake_format import __main__
from cmake_format import configuration
from cmake_format import lexer
from cmake_format import parser
from cmake_format import formatter
from cmake_format.parser import NodeType
from cmake_format.formatter import WrapAlgo


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

  while item_a is not None and item_b is not None:
    yield(item_a, item_b)
    item_a = next(iter_a, None)
    item_b = next(iter_b, None)

  while item_a is not None:
    yield(item_a, None)
    item_a = next(iter_a, None)

  while item_b is not None:
    yield(None, item_b)
    item_b = next(iter_b, None)


def assert_tree(test, nodes, tups, tree=None, history=None):
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
                       formatter.test_string(tree)))
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
    assert_tree(test, node.children, expect_children, tree, subhistory)


class TestCanonicalLayout(unittest.TestCase):
  """
  Given a bunch of example inputs, ensure that the output is as expected.
  """

  def __init__(self, *args, **kwargs):
    super(TestCanonicalLayout, self).__init__(*args, **kwargs)
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

  def tearDown(self):
    pass

  def do_layout_test(self, input_str, expect_tree, strip_len=6):
    """
    Run the formatter on the input string and assert that the result matches
    the output string
    """

    input_str = strip_indent(input_str, strip_len)
    tokens = lexer.tokenize(input_str)
    parse_tree = parser.parse(tokens, self.config.fn_spec)
    box_tree = formatter.layout_tree(parse_tree, self.config)
    assert_tree(self, [box_tree], expect_tree)

  def test_simple_statement(self):
    self.do_layout_test("""\
      cmake_minimum_required(VERSION 2.8.11)
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 38, [
              (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 38, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 22, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 0, 22, 23, []),
                  (NodeType.KWARGGROUP, WrapAlgo.HPACK, 0, 23, 37, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 0, 23, 30, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 31, 37, []),
                  ]),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 0, 37, 38, []),
              ]),
          ]),
      ])

  def test_collapse_additional_newlines(self):
    self.do_layout_test("""\
      # The following multiple newlines should be collapsed into a single newline




      cmake_minimum_required(VERSION 2.8.11)
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 75, [
              (NodeType.COMMENT, WrapAlgo.HPACK, 0, 0, 75, []),
              (NodeType.WHITESPACE, WrapAlgo.HPACK, 1, 0, 0, []),
              (NodeType.STATEMENT, WrapAlgo.HPACK, 2, 0, 38, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 2, 0, 22, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 2, 22, 23, []),
                  (NodeType.KWARGGROUP, WrapAlgo.HPACK, 2, 23, 37, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 2, 23, 30, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 31, 37, []),
                  ]),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 2, 37, 38, []),
              ]),
          ]),
      ])

  def test_multiline_reflow(self):
    self.do_layout_test("""\
      # This multiline-comment should be reflowed
      # into a single comment
      # on one line
      """, [
          (NodeType.BODY, 0, 0, 77, [
              (NodeType.COMMENT, 0, 0, 77, []),
          ])
      ])

  def test_long_args_command_split(self):
    self.do_layout_test("""\
      # This very long command should be split to multiple lines
      set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 58, [
              (NodeType.COMMENT, WrapAlgo.HPACK, 0, 0, 58, []),
              (NodeType.STATEMENT, WrapAlgo.VPACK, 1, 0, 30, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 0, 3, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 1, 3, 4, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 4, 11, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 4, 29, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 3, 4, 29, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 4, 4, 29, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 4, 29, 30, []),
              ]),
          ]),
      ])

  def test_long_arg_on_newline(self):
    self.do_layout_test("""\
      # This command has a very long argument and can't be aligned with the command
      # end, so it should be moved to a new line with block indent + 1.
      some_long_command_name("Some very long argument that really needs to be on the next line.")
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 77, [
              (NodeType.COMMENT, WrapAlgo.HPACK, 0, 0, 77, []),
              (NodeType.STATEMENT, WrapAlgo.KWNVPACK, 2, 0, 70, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 2, 0, 22, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 2, 22, 23, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 3, 2, 69, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 3, 69, 70, []),
              ]),
          ]),
      ])

  def test_argcomment_preserved_and_reflowed(self):
    self.do_layout_test("""\
      set(HEADERS header_a.h header_b.h # This comment should
                                        # be preserved, moreover it should be split
                                        # across two lines.
          header_c.h header_d.h)
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 78, [
              (NodeType.STATEMENT, WrapAlgo.VPACK, 0, 0, 78, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 3, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 0, 3, 4, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 4, 11, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 4, 14, []),
                  (NodeType.ARGUMENT, WrapAlgo.VPACK, 2, 4, 78, [
                      (NodeType.COMMENT, WrapAlgo.HPACK, 2, 15, 78, []),
                  ]),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 4, 4, 14, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 5, 4, 14, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 5, 14, 15, []),
              ]),
          ]),
      ])

  def test_complex_nested_stuff(self):
    self.do_layout_test("""\
      if(foo)
      if(sbar)
      # This comment is in-scope.
      add_library(foo_bar_baz foo.cc bar.cc # this is a comment for arg2
                    # this is more comment for arg2, it should be joined with the first.
          baz.cc) # This comment is part of add_library

      other_command(some_long_argument some_long_argument) # this comment is very long and gets split across some lines

      other_command(some_long_argument some_long_argument some_long_argument) # this comment is even longer and wouldn't make sense to pack at the end of the command so it gets it's own lines
      endif()
      endif()
      """, [
# pylint: disable=bad-continuation
(NodeType.BODY, WrapAlgo.HPACK, 0, 0, 79, [
    (NodeType.FLOW_CONTROL, WrapAlgo.HPACK, 0, 0, 79, [
        (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 7, [
            (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 2, []),
            (NodeType.LPAREN, WrapAlgo.HPACK, 0, 2, 3, []),
            (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 3, 6, []),
            (NodeType.RPAREN, WrapAlgo.HPACK, 0, 6, 7, []),
        ]),
        (NodeType.BODY, WrapAlgo.HPACK, 1, 2, 79, [
            (NodeType.FLOW_CONTROL, WrapAlgo.HPACK, 1, 2, 79, [
                (NodeType.STATEMENT, WrapAlgo.HPACK, 1, 2, 10, [
                    (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 2, 4, []),
                    (NodeType.LPAREN, WrapAlgo.HPACK, 1, 4, 5, []),
                    (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 5, 9, []),
                    (NodeType.RPAREN, WrapAlgo.HPACK, 1, 9, 10, []),
                ]),
                (NodeType.BODY, WrapAlgo.HPACK, 2, 4, 79, [
                    (NodeType.COMMENT, WrapAlgo.HPACK, 2, 4, 31, []),
                    (NodeType.STATEMENT, WrapAlgo.VPACK, 3, 4, 76, [
                        (NodeType.FUNNAME, WrapAlgo.HPACK, 3, 4, 15, []),
                        (NodeType.LPAREN, WrapAlgo.HPACK, 3, 15, 16, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 3, 16, 27, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 4, 16, 22, []),
                        (NodeType.ARGUMENT, WrapAlgo.VPACK, 5, 16, 76, [
                            (NodeType.COMMENT, WrapAlgo.HPACK, 5, 23, 76, []),
                        ]),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 7, 16, 22, []),
                        (NodeType.RPAREN, WrapAlgo.HPACK, 7, 22, 23, []),
                        (NodeType.COMMENT, WrapAlgo.HPACK, 7, 24, 61, []),
                    ]),
                    (NodeType.WHITESPACE, WrapAlgo.HPACK, 8, 4, 0, []),
                    (NodeType.STATEMENT, WrapAlgo.HPACK, 9, 4, 79, [
                        (NodeType.FUNNAME, WrapAlgo.HPACK, 9, 4, 17, []),
                        (NodeType.LPAREN, WrapAlgo.HPACK, 9, 17, 18, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 9, 18, 36, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 9, 37, 55, []),
                        (NodeType.RPAREN, WrapAlgo.HPACK, 9, 55, 56, []),
                        (NodeType.COMMENT, WrapAlgo.HPACK, 9, 57, 79, []),
                    ]),
                    (NodeType.WHITESPACE, WrapAlgo.HPACK, 12, 4, 0, []),
                    (NodeType.STATEMENT, WrapAlgo.VPACK, 13, 4, 79, [
                        (NodeType.FUNNAME, WrapAlgo.HPACK, 13, 4, 17, []),
                        (NodeType.LPAREN, WrapAlgo.HPACK, 13, 17, 18, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 13, 18, 36, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 13, 37, 55, []),
                        (NodeType.ARGUMENT, WrapAlgo.HPACK, 13, 56, 74, []),
                        (NodeType.RPAREN, WrapAlgo.HPACK, 13, 74, 75, []),
                        (NodeType.COMMENT, WrapAlgo.HPACK, 14, 4, 79, []),
                    ]),
                ]),
                (NodeType.STATEMENT, WrapAlgo.HPACK, 16, 2, 9, [
                    (NodeType.FUNNAME, WrapAlgo.HPACK, 16, 2, 7, []),
                    (NodeType.LPAREN, WrapAlgo.HPACK, 16, 7, 8, []),
                    (NodeType.RPAREN, WrapAlgo.HPACK, 16, 8, 9, []),
                ]),
            ]),
        ]),
        (NodeType.STATEMENT, WrapAlgo.HPACK, 17, 0, 7, [
            (NodeType.FUNNAME, WrapAlgo.HPACK, 17, 0, 5, []),
            (NodeType.LPAREN, WrapAlgo.HPACK, 17, 5, 6, []),
            (NodeType.RPAREN, WrapAlgo.HPACK, 17, 6, 7, []),
        ]),
    ]),
]),
      ])

  def test_custom_command(self):
    self.do_layout_test("""\
      # This very long command should be broken up along keyword arguments
      foo(nonkwarg_a nonkwarg_b HEADERS a.h b.h c.h d.h e.h f.h SOURCES a.cc b.cc d.cc DEPENDS foo bar baz)
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 68, [
              (NodeType.COMMENT, WrapAlgo.HPACK, 0, 0, 68, []),
              (NodeType.STATEMENT, WrapAlgo.VPACK, 1, 0, 26, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 0, 3, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 1, 3, 4, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 4, 14, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 15, 25, []),
                  (NodeType.KWARGGROUP, WrapAlgo.VPACK, 2, 4, 15, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 2, 4, 11, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 12, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 3, 12, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 4, 12, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 5, 12, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 6, 12, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 7, 12, 15, []),
                  ]),
                  (NodeType.KWARGGROUP, WrapAlgo.HPACK, 8, 4, 26, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 8, 4, 11, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 8, 12, 16, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 8, 17, 21, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 8, 22, 26, []),
                  ]),
                  (NodeType.KWARGGROUP, WrapAlgo.HPACK, 9, 4, 15, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 9, 4, 11, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 9, 12, 15, []),
                  ]),
                  (NodeType.FLAG, WrapAlgo.HPACK, 10, 4, 7, []),
                  (NodeType.FLAG, WrapAlgo.HPACK, 10, 8, 11, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 10, 11, 12, []),
              ]),
          ]),
      ])

  def test_multiline_string(self):
    self.do_layout_test("""\
      foo(some_arg some_arg "
          This string is on multiple lines
      ")
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 36, [
              (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 36, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 3, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 0, 3, 4, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 4, 12, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 13, 21, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 22, 36, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 2, 1, 2, []),
              ]),
          ]),
      ])

  def test_nested_parens(self):
    self.do_layout_test("""\
      if((NOT HELLO) OR (NOT EXISTS ${WORLD}))
        message(WARNING "something is wrong")
        set(foobar FALSE)
      endif()
      """, [
# pylint: disable=bad-continuation
(NodeType.BODY, WrapAlgo.HPACK, 0, 0, 40, [
    (NodeType.FLOW_CONTROL, WrapAlgo.HPACK, 0, 0, 40, [
        (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 40, [
            (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 2, []),
            (NodeType.LPAREN, WrapAlgo.HPACK, 0, 2, 3, []),
            (NodeType.ARGGROUP, WrapAlgo.HPACK, 0, 3, 14, [
                (NodeType.LPAREN, WrapAlgo.HPACK, 0, 3, 4, []),
                (NodeType.FLAG, WrapAlgo.HPACK, 0, 4, 7, []),
                (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 8, 13, []),
                (NodeType.RPAREN, WrapAlgo.HPACK, 0, 13, 14, []),
            ]),
            (NodeType.KWARGGROUP, WrapAlgo.HPACK, 0, 15, 39, [
                (NodeType.KEYWORD, WrapAlgo.HPACK, 0, 15, 17, []),
                (NodeType.ARGGROUP, WrapAlgo.HPACK, 0, 18, 39, [
                    (NodeType.LPAREN, WrapAlgo.HPACK, 0, 18, 19, []),
                    (NodeType.FLAG, WrapAlgo.HPACK, 0, 19, 22, []),
                    (NodeType.FLAG, WrapAlgo.HPACK, 0, 23, 29, []),
                    (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 30, 38, []),
                    (NodeType.RPAREN, WrapAlgo.HPACK, 0, 38, 39, []),
                ]),
            ]),
            (NodeType.RPAREN, WrapAlgo.HPACK, 0, 39, 40, []),
        ]),
        (NodeType.BODY, WrapAlgo.HPACK, 1, 2, 39, [
            (NodeType.STATEMENT, WrapAlgo.HPACK, 1, 2, 39, [
                (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 2, 9, []),
                (NodeType.LPAREN, WrapAlgo.HPACK, 1, 9, 10, []),
                (NodeType.KWARGGROUP, WrapAlgo.HPACK, 1, 10, 38, [
                    (NodeType.KEYWORD, WrapAlgo.HPACK, 1, 10, 17, []),
                    (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 18, 38, []),
                ]),
                (NodeType.RPAREN, WrapAlgo.HPACK, 1, 38, 39, []),
            ]),
            (NodeType.STATEMENT, WrapAlgo.HPACK, 2, 2, 19, [
                (NodeType.FUNNAME, WrapAlgo.HPACK, 2, 2, 5, []),
                (NodeType.LPAREN, WrapAlgo.HPACK, 2, 5, 6, []),
                (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 6, 12, []),
                (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 13, 18, []),
                (NodeType.RPAREN, WrapAlgo.HPACK, 2, 18, 19, []),
            ]),
        ]),
        (NodeType.STATEMENT, WrapAlgo.HPACK, 3, 0, 7, [
            (NodeType.FUNNAME, WrapAlgo.HPACK, 3, 0, 5, []),
            (NodeType.LPAREN, WrapAlgo.HPACK, 3, 5, 6, []),
            (NodeType.RPAREN, WrapAlgo.HPACK, 3, 6, 7, []),
        ]),
    ]),
]),
      ])

  def test_comment_after_command(self):
    self.do_layout_test("""\
      foo_command() # comment
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 23, [
              (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 23, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 11, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 0, 11, 12, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 0, 12, 13, []),
                  (NodeType.COMMENT, WrapAlgo.HPACK, 0, 14, 23, []),
              ]),
          ]),
      ])

    self.do_layout_test("""\
      foo_command() # this is a long comment that exceeds the desired page width and will be wrapped to a newline
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 78, [
              (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 78, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 11, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 0, 11, 12, []),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 0, 12, 13, []),
                  (NodeType.COMMENT, WrapAlgo.HPACK, 0, 14, 78, []),
              ]),
          ]),
      ])

  def test_arg_just_fits(self):
    """
    Ensure that if an argument *just* fits that it isn't superfluously wrapped
    """

    self.do_layout_test("""\
      message(FATAL_ERROR "81 character line ----------------------------------------")
    """, [
        (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 75, [
            (NodeType.STATEMENT, WrapAlgo.KWNVPACK, 0, 0, 75, [
                (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 7, []),
                (NodeType.LPAREN, WrapAlgo.HPACK, 0, 7, 8, []),
                (NodeType.KWARGGROUP, WrapAlgo.HPACK, 1, 2, 74, [
                    (NodeType.KEYWORD, WrapAlgo.HPACK, 1, 2, 13, []),
                    (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 14, 74, []),
                ]),
                (NodeType.RPAREN, WrapAlgo.HPACK, 1, 74, 75, []),
            ]),
        ]),
    ])

    self.do_layout_test("""\
      message(FATAL_ERROR
              "100 character line ----------------------------------------------------------"
      ) # Closing parenthesis is indented one space!
    """, [
        (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 83, [
            (NodeType.STATEMENT, WrapAlgo.PNVPACK, 0, 0, 83, [
                (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 7, []),
                (NodeType.LPAREN, WrapAlgo.HPACK, 0, 7, 8, []),
                (NodeType.KWARGGROUP, WrapAlgo.PNVPACK, 1, 2, 83, [
                    (NodeType.KEYWORD, WrapAlgo.HPACK, 1, 2, 13, []),
                    (NodeType.ARGUMENT, WrapAlgo.PNVPACK, 2, 4, 83, []),
                ]),
                (NodeType.RPAREN, WrapAlgo.HPACK, 3, 2, 3, []),
                (NodeType.COMMENT, WrapAlgo.HPACK, 3, 4, 48, []),
            ]),
        ]),
    ])

    self.do_layout_test("""\
      message(
        "100 character line ----------------------------------------------------------------------"
        ) # Closing parenthesis is indented one space!
    """, [
        (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 93, [
            (NodeType.STATEMENT, WrapAlgo.PNVPACK, 0, 0, 93, [
                (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 7, []),
                (NodeType.LPAREN, WrapAlgo.HPACK, 0, 7, 8, []),
                (NodeType.ARGUMENT, WrapAlgo.PNVPACK, 1, 2, 93, []),
                (NodeType.RPAREN, WrapAlgo.HPACK, 2, 2, 3, []),
                (NodeType.COMMENT, WrapAlgo.HPACK, 2, 4, 48, []),
            ]),
        ]),
    ])

  def test_string_preserved_during_split(self):
    self.do_layout_test("""\
      # The string in this command should not be split
      set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 74, [
              (NodeType.COMMENT, WrapAlgo.HPACK, 0, 0, 48, []),
              (NodeType.STATEMENT, WrapAlgo.VPACK, 1, 0, 74, [
                  (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 0, 21, []),
                  (NodeType.LPAREN, WrapAlgo.HPACK, 1, 21, 22, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 22, 25, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 26, 29, []),
                  (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 30, 33, []),
                  (NodeType.KWARGGROUP, WrapAlgo.HPACK, 2, 22, 73, [
                      (NodeType.KEYWORD, WrapAlgo.HPACK, 2, 22, 32, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 33, 46, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 2, 47, 73, []),
                  ]),
                  (NodeType.RPAREN, WrapAlgo.HPACK, 2, 73, 74, []),
              ]),
          ]),
      ])

  def test_while(self):
    self.do_layout_test("""\
      while(forbarbaz arg1 arg2, arg3)
        message(hello ${foobarbaz})
      endwhile()
      """, [
          (NodeType.BODY, WrapAlgo.HPACK, 0, 0, 32, [
              (NodeType.FLOW_CONTROL, WrapAlgo.HPACK, 0, 0, 32, [
                  (NodeType.STATEMENT, WrapAlgo.HPACK, 0, 0, 32, [
                      (NodeType.FUNNAME, WrapAlgo.HPACK, 0, 0, 5, []),
                      (NodeType.LPAREN, WrapAlgo.HPACK, 0, 5, 6, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 6, 15, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 16, 20, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 21, 26, []),
                      (NodeType.ARGUMENT, WrapAlgo.HPACK, 0, 27, 31, []),
                      (NodeType.RPAREN, WrapAlgo.HPACK, 0, 31, 32, []),
                  ]),
                  (NodeType.BODY, WrapAlgo.HPACK, 1, 2, 29, [
                      (NodeType.STATEMENT, WrapAlgo.HPACK, 1, 2, 29, [
                          (NodeType.FUNNAME, WrapAlgo.HPACK, 1, 2, 9, []),
                          (NodeType.LPAREN, WrapAlgo.HPACK, 1, 9, 10, []),
                          (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 10, 15, []),
                          (NodeType.ARGUMENT, WrapAlgo.HPACK, 1, 16, 28, []),
                          (NodeType.RPAREN, WrapAlgo.HPACK, 1, 28, 29, []),
                      ]),
                  ]),
                  (NodeType.STATEMENT, WrapAlgo.HPACK, 2, 0, 10, [
                      (NodeType.FUNNAME, WrapAlgo.HPACK, 2, 0, 8, []),
                      (NodeType.LPAREN, WrapAlgo.HPACK, 2, 8, 9, []),
                      (NodeType.RPAREN, WrapAlgo.HPACK, 2, 9, 10, []),
                  ]),
              ]),
          ]),
      ])

if __name__ == '__main__':
  format_str = '[%(levelname)-4s] %(filename)s:%(lineno)-3s: %(message)s'
  logging.basicConfig(level=logging.DEBUG,
                      format=format_str,
                      datefmt='%Y-%m-%d %H:%M:%S',
                      filemode='w')
  unittest.main()
