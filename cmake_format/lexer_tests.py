# -*- coding: utf-8 -*-
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
    self.assert_tok_types("foo(bar [=[hello world]=] baz)", [
        lexer.WORD, lexer.LEFT_PAREN, lexer.WORD,
        lexer.WHITESPACE, lexer.BRACKET_ARGUMENT, lexer.WHITESPACE,
        lexer.WORD, lexer.RIGHT_PAREN])

  def test_bracket_comments(self):
    self.assert_tok_types("foo(bar #[=[hello world]=] baz)", [
        lexer.WORD, lexer.LEFT_PAREN, lexer.WORD,
        lexer.WHITESPACE, lexer.BRACKET_COMMENT, lexer.WHITESPACE,
        lexer.WORD, lexer.RIGHT_PAREN])

    self.assert_tok_types("""\
      #[==[This is a bracket comment at some nested level
      #    it is preserved verbatim, but trailing
      #    whitespace is removed.]==]
      """, [lexer.WHITESPACE, lexer.BRACKET_COMMENT, lexer.NEWLINE,
            lexer.WHITESPACE])


if __name__ == '__main__':
  unittest.main()
