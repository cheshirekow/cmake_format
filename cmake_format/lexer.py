from __future__ import print_function

import re

# NOTE(josh): inspiration and some bits taken from cmakeast_ and
# cmakelistparsing_
#
# .. _cmake_ast: https://github.com/polysquare/cmake-ast
# .. _cmakelist_parsing: https://github.com/ijt/cmakelists_parsing


# Token types... enum is slow
QUOTED_LITERAL = 0
LEFT_PAREN = 1
RIGHT_PAREN = 2
WORD = 3
NUMBER = 4
DEREF = 5
WHITESPACE = 6
NEWLINE = 7
COMMENT = 8
UNQUOTED_LITERAL = 9
FORMAT_OFF = 10
FORMAT_ON = 11
BRACKET_ARGUMENT = 12
BRACKET_COMMENT = 13


def token_type_to_str(query):
  """
  Return the string name of a token type enum value.
  """
  for name, value in globals().items():
    if name[0].upper() == name[0] and value == query:
      return name
  return None


class Token(object):
  """
  Lexical unit of a listfile.
  """

  def __init__(self, tok_type, content, line, col, index):
    self.type = tok_type
    self.content = content
    self.line = line
    self.col = col
    self.index = index

  def __repr__(self):
    """A string representation of this token."""
    return ("Token(type={0}, "
            "content={1}, "
            "line={2}, "
            "col={3})").format(token_type_to_str(self.type),
                               self.content,
                               self.line,
                               self.col)


def tokenize(contents):
  """
  Scan a string and return a list of Token objects representing the contents
  of the cmake listfile.
  """
  # Regexes are in priority order. Changing the order may alter the
  # behavior of the lexer
  scanner = re.Scanner([
      # double quoted string
      (r'(?<![^\s\(])"([^\"]|\\[\"])*[^\\]?"(?![^\s\)])',
       lambda s, t: (QUOTED_LITERAL, t)),
      # single quoted string
      (r"(?<![^\s\(])'([^\']|\\[\'])*[^\\]?'(?![^\s\)])",
       lambda s, t: (QUOTED_LITERAL, t)),
      # bracket argument
      (r"(?<![^\s\(])\[(=*)\[.*\]\1\](?![^\s\)])",
       lambda s, t: (BRACKET_ARGUMENT, t)),
      (r"(?<![^\s\(])-?[0-9]+(?![^\s\)\(])",
       lambda s, t: (NUMBER, t)),
      (r"\(", lambda s, t: (LEFT_PAREN, t)),
      (r"\)", lambda s, t: (RIGHT_PAREN, t)),
      # Either a valid function name or variable name.
      (r"(?<![^\s\(])[a-zA-z_][a-zA-Z0-9_]*(?![^\s\)\(])",
       lambda s, t: (WORD, t)),
      # Variable dereference. Borrowed from cmakeast.
      # NOTE(josh): I don't think works for nested derefs.
      (r"(?<![^\s\(])\${[a-zA-z_][a-zA-Z0-9_]*}(?![^\s\)])",
       lambda s, t: (DEREF, t)),
      # NOTE(josh): bare carriage returns are very unlikely to be used but
      # just for the case of explicitnes, if we ever encounter any we treat
      # it as a newline
      (r"\r?\n", lambda s, t: (NEWLINE, t)),
      (r"\r\n?", lambda s, t: (NEWLINE, t)),
      # NOTE(josh): don't match '\s' here or we'll miss some newline tokens
      # TODO(josh): should we match unicode whitespace too?
      (r"[ \t\f\v]+", lambda s, t: (WHITESPACE, t)),
      (r"#\s*cmake-format: off[^\n]*", lambda s, t: (FORMAT_OFF, t)),
      (r"#\s*cmake-format: on[^\n]*", lambda s, t: (FORMAT_ON, t)),
      # bracket comment
      (r"#\[(=*)\[.*\]\1\]", lambda s, t: (BRACKET_COMMENT, t)),
      # line comment
      (r"#[^\n]*", lambda s, t: (COMMENT, t)),
      # Catch-all for literals which are compound statements.
      (r"([^\s\(\)]+|[^\s\(]*[^\)]|[^\(][^\s\)]*)",
       lambda s, t: (UNQUOTED_LITERAL, t))
  ], re.DOTALL)

  tokens, remainder = scanner.scan(contents)
  assert not remainder, "Unparsed tokens: {}".format(remainder)

  # Now add line, column, and serial number to token objects. We get lineno
  # by maintaining a running count of newline characters encountered among
  # tokens so far, and column count by splitting the most recent token on
  # it's right most newline. Note that line and numbers are 1-indexed to match
  # up with editors but column numbers are zero indexed because its fun to be
  # inconsistent.
  tokens_return = []
  lineno = 1
  col = 0
  for token_index, (token_type, token_contents) in enumerate(tokens):
    tokens_return.append(Token(tok_type=token_type,
                               content=token_contents,
                               line=lineno,
                               col=col,
                               index=token_index))
    newlines = token_contents.count('\n')
    lineno += newlines
    if newlines:
      col = len(token_contents.rsplit('\n', 1)[1])
    else:
      col += len(token_contents)

  return tokens_return


def parse_bracket_argument(text):
  regex = re.compile(r'^\[(=*)\[(.*)\]\1\]$', re.DOTALL)
  match = regex.match(text)
  assert match, "Failed to match bracket argument pattern in {}".format(text)
  return ('[' + match.group(1) + '[',
          match.group(2),
          ']' + match.group(1) + ']')


def parse_bracket_comment(text):
  prefix, content, suffix = parse_bracket_argument(text[1:])
  return ('#' + prefix, content, suffix)


def main():
  """
  Dump tokenized listfile to stdout for debugging.
  """
  import argparse
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('infile')
  args = parser.parse_args()
  with open(args.infile, 'r') as infile:
    tokens = tokenize(infile.read())
  print('\n'.join(str(x) for x in tokens))


if __name__ == '__main__':
  main()
