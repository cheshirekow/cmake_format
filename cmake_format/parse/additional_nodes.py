# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import logging

from cmake_format import lexer
from cmake_format.parse.util import (
    WHITESPACE_TOKENS, pargs_are_full, should_break, get_normalized_kwarg
)
from cmake_format.parse.common import (
    NodeType, TreeNode,
)
from cmake_format.parse.simple_nodes import CommentNode
from cmake_format.parse.argument_nodes import (
    PositionalGroupNode, PositionalParser, StandardArgTree
)

logger = logging.getLogger(__name__)

# pylint: disable=W0221


class TupleGroupNode(PositionalGroupNode):
  """A positinal argument group where each argument is a tuple of tokens."""

  @classmethod
  def parse(cls, ctx, tokens, npargs, ntup, flags, breakstack):
    """Parse a continuous sequence of `npargs` positional argument pairs.
    If npargs is an integer we will consume exactly that many arguments.
    If it is not an integer then it is a string meaning:

    * "?": zero or one
    * "*": zero or more
    * "+": one or more
    """

    tree = TreeNode(NodeType.PARGGROUP)
    subtree = None
    active_depth = tree

    npargs_consumed = 0
    ntup_consumed = 0

    while tokens:
      # Break if we have consumed enough positional arguments
      if pargs_are_full(npargs, npargs_consumed):
        break

      # Break if the next token belongs to a parent parser, i.e. if it
      # matches a keyword argument of something higher in the stack, or if
      # it closes a parent group.
      if should_break(tokens[0], breakstack):
        break

      # Otherwise we will consume the token
      token = tokens.pop(0)

      # If it is a whitespace token then put it directly in the parse tree at
      # the current depth
      if token.type in WHITESPACE_TOKENS:
        active_depth.children.append(token)
        continue

      # If it's a comment token not associated with an argument, then put it
      # directly into the parse tree at the current depth
      if token.type in (lexer.TokenType.COMMENT,
                        lexer.TokenType.BRACKET_COMMENT):
        child = TreeNode(NodeType.COMMENT)
        tree.children.append(child)
        child.children.append(token)
        continue

      if subtree is None:
        subtree = TreeNode(NodeType.PARGGROUP)
        tree.children.append(subtree)
        ntup_consumed = 0

      # Otherwise is it is a positional argument, so add it to the tree as such
      if get_normalized_kwarg(token) in flags:
        child = TreeNode(NodeType.FLAG)
      else:
        child = TreeNode(NodeType.ARGUMENT)

      child.children.append(token)
      CommentNode.consume_trailing(ctx, tokens, child)
      subtree.children.append(child)
      ntup_consumed += 1

      if ntup_consumed >= ntup:
        npargs_consumed += 1
        subtree = None

    return tree


class TupleParser(object):
  def __init__(self, ntup, npargs=None, flags=None):
    if npargs is None:
      npargs = "*"
    if flags is None:
      flags = []

    self.npargs = npargs
    self.ntup = ntup
    self.flags = flags

  def __call__(self, ctx, tokens, breakstack):
    return TupleGroupNode.parse(
        ctx, tokens, self.npargs, self.ntup, self.flags, breakstack)


class ShellCommandNode(StandardArgTree):
  """Shell commands are children of a `COMMAND` keyword argument and are
     common enough to warrant their own node. We also will likely want some
     special formatting rules for these nodes.
  """

  @classmethod
  def parse(cls, ctx, tokens, breakstack):
    """
    Parser for the COMMAND kwarg lists in the form of::

        COMMAND foo --long-flag1 arg1 arg2 --long-flag2 -a -b -c arg3 arg4

    The parser acts very similar to a standard parser where `--xxx` is treated
    as a keyword argument and `-x` is treated as a flag.
    """
    return super(ShellCommandNode, cls).parse(
        ctx, tokens, '*', {}, [], breakstack)


class PatternNode(StandardArgTree):
  """Patterns are children of a `PATTERN` keyword argument and are common
     enough to warrent their own node."""

  @classmethod
  def parse(cls, ctx, tokens, breakstack):
    """
    ::

      [PATTERN <pattern> | REGEX <regex>]
      [EXCLUDE] [PERMISSIONS <permissions>...]
    """
    return super(PatternNode, cls).parse(
        ctx, tokens,
        npargs='+',
        kwargs={"PERMISSIONS": PositionalParser('+'), },
        flags=["EXCLUDE"],
        breakstack=breakstack
    )


class FlagGroupNode(PositionalGroupNode):
  """A positinal group where each argument is a flag."""

  @classmethod
  def parse(cls, ctx, tokens, flags, breakstack):
    """
    Parse a continuous sequence of flags
    """

    # TODO(josh): use a bespoke FLAGGROUP?
    tree = cls()
    while tokens:
      # Break if the next token belongs to a parent parser, i.e. if it
      # matches a keyword argument of something higher in the stack, or if
      # it closes a parent group.
      if should_break(tokens[0], breakstack):
        break

      # If it is a whitespace token then put it directly in the parse tree at
      # the current depth
      if tokens[0].type in WHITESPACE_TOKENS:
        tree.children.append(tokens.pop(0))
        continue

      # Break if the next token is not a known flag
      if tokens[0].spelling.upper() not in flags:
        break

      # Otherwise is it is a flag, so add it to the tree as such
      child = TreeNode(NodeType.FLAG)
      child.children.append(tokens.pop(0))
      CommentNode.consume_trailing(ctx, tokens, child)
      tree.children.append(child)

    return tree
