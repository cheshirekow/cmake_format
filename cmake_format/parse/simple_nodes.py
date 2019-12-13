# -*- coding: utf-8 -*-
# pylint: disable=W0613
from __future__ import print_function
from __future__ import unicode_literals

import logging

from cmake_format import lexer
from cmake_format.parse.util import (
    COMMENT_TOKENS, WHITESPACE_TOKENS,
    are_column_aligned, next_is_trailing_comment, is_valid_trailing_comment
)
from cmake_format.parse.common import NodeType, TreeNode

logger = logging.getLogger(__name__)


class WhitespaceNode(TreeNode):
  """Stores a sequence of whitespace tokens at body scope."""

  def __init__(self):
    super(WhitespaceNode, self).__init__(NodeType.WHITESPACE)

  @classmethod
  def consume(cls, ctx, tokens):
    """
    Consume sequential whitespace, removing tokens from the input list and
    returning a whitespace BlockNode
    """
    node = cls()
    while tokens and tokens[0].type in WHITESPACE_TOKENS:
      node.children.append(tokens.pop(0))
    return node


class CommentNode(TreeNode):
  """Stores a sequence of one or more comment tokens separated by at most
     one newline. These comment tokens together form one semantic comment."""

  def __init__(self):
    super(CommentNode, self).__init__(NodeType.COMMENT)

  @classmethod
  def consume(cls, ctx, tokens):
    """
    Consume sequential comment lines, removing tokens from the input list and
    returning a comment Block
    """

    node = cls()
    if tokens[0].type == lexer.TokenType.BRACKET_COMMENT:
      # Bracket comments get their own node because they are caapable of
      # globbing up their newlines. Thus they are their own semantic comment,
      # and are not part of any larger semantic structures.
      node.children.append(tokens.pop(0))
      return node

    comment_tokens = []
    while tokens and tokens[0].type in COMMENT_TOKENS:
      # If the next comment token is not column-aligned, then we don't
      # merge it with the previous comment line
      if (comment_tokens and
          not are_column_aligned(comment_tokens[-1], tokens[0])):
        break

      comment_token = tokens.pop(0)
      comment_tokens.append(comment_token)
      node.children.append(comment_token)

      # Multiple comments separated by only one newline are joined together into
      # a single block
      if (len(tokens) > 1
          # pylint: disable=bad-continuation
          and tokens[0].type == lexer.TokenType.NEWLINE
          and tokens[1].type in COMMENT_TOKENS):
        node.children.append(tokens.pop(0))

      # Multiple comments separated only by one newline and some whitespace are
      # joined together into a single block
      elif (len(tokens) > 2
            # pylint: disable=bad-continuation
            and tokens[0].type == lexer.TokenType.NEWLINE
            and tokens[1].type == lexer.TokenType.WHITESPACE
            and tokens[2].type in COMMENT_TOKENS):
        node.children.append(tokens.pop(0))
        node.children.append(tokens.pop(0))

    return node

  @classmethod
  def consume_trailing(cls, ctx, tokens, parent):
    """
    Consume sequential comment lines, removing tokens from the input list and
    appending the resulting node as a child to the provided parent
    """
    if not next_is_trailing_comment(tokens):
      return

    if tokens[0].type == lexer.TokenType.WHITESPACE:
      parent.children.append(tokens.pop(0))

    node = TreeNode(NodeType.COMMENT)
    parent.children.append(node)
    comment_tokens = node.children

    comment_tokens = []
    while tokens and is_valid_trailing_comment(tokens[0]):
      if (comment_tokens and
          not are_column_aligned(comment_tokens[-1], tokens[0])):
        break

      comment_token = tokens.pop(0)
      comment_tokens.append(comment_token)
      node.children.append(comment_token)

      # Multiple comments separated by only one newline are joined together into
      # a single block
      if (len(tokens) > 1 and
          tokens[0].type == lexer.TokenType.NEWLINE and
          is_valid_trailing_comment(tokens[1])):
        node.children.append(tokens.pop(0))

      # Multiple comments separated only by one newline and some whitespace are
      # joined together into a single block
      # TODO(josh)[873a811]: maybe match only on comment tokens that start at
      # the same column?
      elif (len(tokens) > 2 and
            tokens[0].type == lexer.TokenType.NEWLINE and
            tokens[1].type == lexer.TokenType.WHITESPACE and
            is_valid_trailing_comment(tokens[2])):
        node.children.append(tokens.pop(0))
        node.children.append(tokens.pop(0))


class OnOffNode(TreeNode):
  """Stores a single comment token signifying cmake-format should enable or
     disable.
  """

  def __init__(self):
    super(OnOffNode, self).__init__(NodeType.ONOFFSWITCH)

  @classmethod
  def consume(cls, ctx, tokens):
    """
    Consume a 'cmake-format: [on|off]' comment
    """

    node = cls()
    node.children.append(tokens.pop(0))
    return node


def consume_whitespace_and_comments(tokens, tree):
  """Consume any whitespace or comments that occur at the current depth
  """
  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens:
    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(tokens.pop(0))
      continue
    break
