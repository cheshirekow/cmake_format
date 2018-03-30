# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from cmake_format import __main__
from cmake_format import lexer


class TestSpecificLexings(unittest.TestCase):

  def assert_tok_types(self, input_str, expected_types):
    """
    Run the lexer on the input string and assert that the result tokens match
    the expected
    """

    self.assertEqual(expected_types,
                     [tok.type for tok in lexer.tokenize(input_str)])

  def test_bracket_arguments(self):
    self.assert_tok_types(u"foo(bar [=[hello world]=] baz)", [
        lexer.WORD, lexer.LEFT_PAREN, lexer.WORD,
        lexer.WHITESPACE, lexer.BRACKET_ARGUMENT, lexer.WHITESPACE,
        lexer.WORD, lexer.RIGHT_PAREN])

  def test_bracket_comments(self):
    self.assert_tok_types(u"foo(bar #[=[hello world]=] baz)", [
        lexer.WORD, lexer.LEFT_PAREN, lexer.WORD,
        lexer.WHITESPACE, lexer.BRACKET_COMMENT, lexer.WHITESPACE,
        lexer.WORD, lexer.RIGHT_PAREN])

    self.assert_tok_types(u"""\
      #[==[This is a bracket comment at some nested level
      #    it is preserved verbatim, but trailing
      #    whitespace is removed.]==]
      """, [lexer.WHITESPACE, lexer.BRACKET_COMMENT, lexer.NEWLINE,
            lexer.WHITESPACE])

  def test_string(self):
    self.assert_tok_types(u"""\
      foo(bar "this is a string")
      """, [lexer.WHITESPACE, lexer.WORD, lexer.LEFT_PAREN, lexer.WORD,
            lexer.WHITESPACE, lexer.QUOTED_LITERAL, lexer.RIGHT_PAREN,
            lexer.NEWLINE, lexer.WHITESPACE])

  def test_string_with_quotes(self):
    self.assert_tok_types(r"""
      "this is a \"string"
      """, [lexer.NEWLINE, lexer.WHITESPACE, lexer.QUOTED_LITERAL,
            lexer.NEWLINE, lexer.WHITESPACE])

    self.assert_tok_types(r"""
      'this is a \'string'
      """, [lexer.NEWLINE, lexer.WHITESPACE, lexer.QUOTED_LITERAL,
            lexer.NEWLINE, lexer.WHITESPACE])

  def test_complicated_string_with_quotes(self):
    # NOTE(josh): compacted example from bug report
    # https://github.com/cheshirekow/cmake_format/issues/28
    self.assert_tok_types(r"""
      install(CODE "message(\"foo ${bar}/${baz}...\")
        subfun(COMMAND ${WHEEL_COMMAND}
                       ERROR_MESSAGE \"error ${bar}/${baz}\"
               )"
      )
      """, [lexer.NEWLINE, lexer.WHITESPACE, lexer.WORD, lexer.LEFT_PAREN,
            lexer.WORD, lexer.WHITESPACE, lexer.QUOTED_LITERAL,
            lexer.NEWLINE, lexer.WHITESPACE, lexer.RIGHT_PAREN, lexer.NEWLINE,
            lexer.WHITESPACE])

  def test_mixed_whitespace(self):
    """
    Ensure that if a newline is part of a whitespace sequence then it is
    tokenized separately.
    """
    self.assert_tok_types(u" \n", [lexer.WHITESPACE, lexer.NEWLINE])
    self.assert_tok_types(u"\t\n", [lexer.WHITESPACE, lexer.NEWLINE])
    self.assert_tok_types(u"\f\n", [lexer.WHITESPACE, lexer.NEWLINE])
    self.assert_tok_types(u"\v\n", [lexer.WHITESPACE, lexer.NEWLINE])
    self.assert_tok_types(u"\r\n", [lexer.NEWLINE])


if __name__ == '__main__':
  unittest.main()
