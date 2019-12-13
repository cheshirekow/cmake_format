# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from __future__ import print_function
from __future__ import unicode_literals

from cmake_format.parse.body_nodes import BodyNode


class MockEverything(object):
  """Dummy object which implements any interface by mocking all functions
     with an empty implementation that returns None"""

  # pylint: disable=unused-argument
  def _dummy(self, *_args, **_kwargs):
    return

  def __getattr__(self, _name):
    return self._dummy


class ParseContext(object):
  """Global context passed through every function in the parse stack."""

  def __init__(self, parse_db=None, lint_ctx=None):
    if parse_db is None:
      from cmake_format import parse_funs
      parse_db = parse_funs.get_parse_db()
    self.parse_db = parse_db

    if lint_ctx is None:
      lint_ctx = MockEverything()
    self.lint_ctx = lint_ctx


def parse(tokens, ctx=None):
  """
  digest tokens, then layout the digested blocks.
  """
  if ctx is None:
    ctx = ParseContext()
  return BodyNode.consume(ctx, tokens)
