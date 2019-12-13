# -*- coding: utf-8 -*-
# pylint: disable=W0613
from __future__ import print_function
from __future__ import unicode_literals

import logging

from cmake_format import lexer
from cmake_format.parse.util import COMMENT_TOKENS, WHITESPACE_TOKENS
from cmake_format.parse.common import NodeType, ParenBreaker, TreeNode
from cmake_format.parse.printer import tree_string
from cmake_format.parse.argument_nodes import StandardParser
from cmake_format.parse.simple_nodes import CommentNode


logger = logging.getLogger(__name__)


class FunctionNameNode(TreeNode):
  def __init__(self):
    super(FunctionNameNode, self).__init__(NodeType.FUNNAME)
    self.token = None

  @classmethod
  def parse(cls, ctx, tokens):
    node = cls()
    node.token = tokens.pop(0)
    node.children.append(node.token)
    return node


class StatementNode(TreeNode):
  """Parent node of a statement subtree."""

  def __init__(self):
    super(StatementNode, self).__init__(NodeType.STATEMENT)
    self.funnode = None
    self.argtree = None

  def get_funname(self):
    return self.funnode.token.spelling.lower()

  @classmethod
  def consume(cls, ctx, tokens):
    """
    Consume a complete statement, removing tokens from the input list and
    returning a STATEMENT node.
    """
    node = cls()

    # Consume the function name
    fnname = tokens[0].spelling.lower()
    node.funnode = funnode = FunctionNameNode.parse(ctx, tokens)
    node.children.append(funnode)

    # Consume whitespace up to the parenthesis
    while tokens and tokens[0].type in WHITESPACE_TOKENS:
      node.children.append(tokens.pop(0))

    # TODO(josh): should the parens belong to the statement node or the
    # group node?
    if tokens[0].type != lexer.TokenType.LEFT_PAREN:
      raise ValueError(
          "Unexpected {} token at {}, expecting l-paren, got {}"
          .format(tokens[0].type.name, tokens[0].get_location(),
                  repr(tokens[0].content)))

    lparen = TreeNode(NodeType.LPAREN)
    lparen.children.append(tokens.pop(0))
    node.children.append(lparen)

    while tokens and tokens[0].type in WHITESPACE_TOKENS:
      node.children.append(tokens.pop(0))
      continue

    breakstack = [ParenBreaker()]

    parse_fun = ctx.parse_db.get(fnname, None)
    if parse_fun is None:
      # If the parse_db provides a "_default" then use that. Otherwise use the
      # standard parser with no kwargs or flags.
      parse_fun = ctx.parse_db.get("_default", StandardParser())
    node.argtree = subtree = parse_fun(ctx, tokens, breakstack)
    node.children.append(subtree)

    # NOTE(josh): technically we may have a statement specification with
    # an exact number of arguments. At this point we have broken out of that
    # statement but we might have some comments or whitespace to consume
    while tokens and tokens[0].type != lexer.TokenType.RIGHT_PAREN:
      if tokens[0].type in WHITESPACE_TOKENS:
        node.children.append(tokens.pop(0))
        continue

      if tokens[0].type in COMMENT_TOKENS:
        cnode = CommentNode.consume(ctx, tokens)
        node.children.append(cnode)
        continue

      raise ValueError(
          "Unexpected {} token at {}, expecting r-paren, got {}"
          .format(tokens[0].type.name, tokens[0].get_location(),
                  repr(tokens[0].content)))

    assert tokens, (
        "Unexpected end of token stream while parsing statement:\n {}"
        .format(tree_string([node])))
    assert tokens[0].type == lexer.TokenType.RIGHT_PAREN, (
        "Unexpected {} token at {}, expecting r-paren, got {}"
        .format(tokens[0].type.name, tokens[0].get_location(),
                repr(tokens[0].content)))

    rparen = TreeNode(NodeType.RPAREN)
    rparen.children.append(tokens.pop(0))
    node.children.append(rparen)
    CommentNode.consume_trailing(ctx, tokens, node)

    return node
