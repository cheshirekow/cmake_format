# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys

from cmake_format.tools.usage_lexer import TokenType, Token, tokenize

logger = logging.getLogger(__name__)


class ChoiceNode(list):
  def __init__(self, required=False):
    super(ChoiceNode, self).__init__()
    self.required = required
    self.append([])

  def __repr__(self):
    tags = []
    if self.required:
      tags.append("required")
    else:
      tags.append("optional")
    return "node {}".format(tags)


def parse(tokens):
  """
  Parse a token stream into a tree of nodes
  """

  parse_stack = [ChoiceNode(required=True)]
  for token in tokens:
    if token.type is TokenType.WHITESPACE:
      continue
    elif token.type is TokenType.LPAREN:
      next_group = ChoiceNode(required=True)
      parse_stack[-1][-1].append(next_group)
      parse_stack.append(next_group)
    elif token.type is TokenType.LSQ_BRACKET:
      next_group = ChoiceNode(required=False)
      parse_stack[-1][-1].append(next_group)
      parse_stack.append(next_group)
    elif token.type is TokenType.LA_BRACKET:
      next_group = ChoiceNode(required=True)
      parse_stack[-1][-1].append(next_group)
      parse_stack.append(next_group)
    elif token.type in (TokenType.RSQ_BRACKET, TokenType.RA_BRACKET,
                        TokenType.RPAREN):
      parse_stack.pop(-1)
    elif token.type is TokenType.PIPE:
      parse_stack[-1].append([])
    else:
      parse_stack[-1][-1].append(token)
  return parse_stack[0]


def dump_tree(nodes, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for idx, node in enumerate(nodes):
    outfile.write(indent)
    if idx + 1 == len(nodes):
      outfile.write('└─ ')
      increment = '    '
    else:
      outfile.write('├─ ')
      increment = '│   '

    if isinstance(node, (Token, ChoiceNode)):
      linestr = repr(node)
    elif isinstance(node, list):
      linestr = "choice {}".format(idx)
    else:
      raise ValueError("Unexpected node type {}".format(type(node)))
    outfile.write(linestr)
    outfile.write('\n')

    if isinstance(node, Token):
      continue

    if isinstance(node, ChoiceNode) and len(node) == 1:
      dump_tree(node[0], outfile, indent + increment)
      continue

    dump_tree(node, outfile, indent + increment)


def main():
  """
  Dump parse tree for debugging
  """
  import argparse
  import io
  import os

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('infile')
  args = parser.parse_args()

  infile_arg = args.infile
  if args.infile == "-":
    infile_arg = os.dup(sys.stdin.fileno())

  with io.open(infile_arg, 'r') as infile:
    tokens = tokenize(infile.read())
  parse_tree = parse(tokens)
  dump_tree([parse_tree])


if __name__ == '__main__':
  main()
