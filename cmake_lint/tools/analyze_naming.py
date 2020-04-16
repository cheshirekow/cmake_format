# -*- coding: utf-8 -*-
"""
Analyze the naming conventions by recording all variable assignments and
classifying them according to context.
"""

from __future__ import unicode_literals

import argparse
import io
import logging
import os
import re
import sys

import cmake_format
from cmake_format import common
from cmake_format import __main__
from cmake_format import configuration
from cmake_format import lexer
from cmake_format import parse
from cmake_format import parse_funs

from cmake_format.lexer import TokenType
from cmake_lint.basic_checker import (
    Scope, get_scope_of_assignment, find_statements_in_subtree)

logger = logging.getLogger(__name__)


class NameCollector(object):
  def __init__(self):
    self.varnames = []

  def collect_names(self, parse_tree):
    for stmt in find_statements_in_subtree(parse_tree, ["set", "list"]):
      scope = get_scope_of_assignment(stmt)
      if stmt.get_funname() == "set":
        token = stmt.argtree.varname
      else:
        token = stmt.argtree.parg_groups[0].get_tokens(kind="semantic")[1]
      self.varnames.append((scope, token.spelling))

    for stmt in find_statements_in_subtree(parse_tree, ["foreach"]):
      tokens = stmt.get_semantic_tokens()
      tokens.pop(0)  # statement name "foreach"
      tokens.pop(0)  # lparen
      token = tokens.pop(0)  # loopvar
      self.varnames.append((Scope.LOOP, token.spelling))

    for stmt in find_statements_in_subtree(parse_tree, ["function", "macro"]):
      tokens = stmt.argtree.get_semantic_tokens()[1:]
      for token in tokens:  # named arguments
        if token.type is TokenType.RIGHT_PAREN:
          break
        if token.type is not TokenType.WORD:
          logger.warning(
              "Unexpected token %s at %s", token.spelling, token.get_location())
        else:
          self.varnames.append((Scope.ARGUMENT, token.spelling))


def setup_argparse(argparser):
  argparser.add_argument('-v', '--version', action='version',
                         version=cmake_format.VERSION)
  argparser.add_argument(
      '-l', '--log-level', default="info",
      choices=["error", "warning", "info", "debug"])

  argparser.add_argument(
      '-o', '--outfile-path', default=None,
      help='Write errors to this file. Default is stdout.')

  argparser.add_argument('infilepaths', nargs='*')


USAGE_STRING = """
analyze_naming [-h] [-o OUTFILE_PATH] infilepath [infilepath ...]
"""


def inner_main():
  """Parse arguments, open files, start work."""
  logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

  argparser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      usage=USAGE_STRING)

  setup_argparse(argparser)
  args = argparser.parse_args()
  logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

  if args.outfile_path is None:
    args.outfile_path = '-'

  if '-' in args.infilepaths:
    assert len(args.infilepaths) == 1, \
        "You cannot mix stdin as an input with other input files"

  if args.outfile_path == '-':
    outfile = io.open(os.dup(sys.stdout.fileno()),
                      mode='w', encoding="utf-8", newline='')
  else:
    outfile = io.open(args.outfile_path, 'w', encoding="utf-8", newline='')

  returncode = 0

  cfg = configuration.Configuration()
  collector = NameCollector()
  for infile_path in args.infilepaths:
    # NOTE(josh): have to load config once for every file, because we may pick
    # up a new config file location for each path
    if infile_path == '-':
      infile_path = os.dup(sys.stdin.fileno())

    try:
      infile = io.open(
          infile_path, mode='r', encoding=cfg.encode.input_encoding, newline='')
    except (IOError, OSError):
      logger.error("Failed to open %s for read", infile_path)
      returncode = 1
      continue

    try:
      with infile:
        infile_content = infile.read()
    except UnicodeDecodeError:
      logger.error(
          "Unable to read %s as %s", infile_path, cfg.encode.input_encoding)
      returncode = 1
      continue

    tokens = lexer.tokenize(infile_content)
    parse_db = parse_funs.get_parse_db()
    ctx = parse.ParseContext(parse_db, config=cfg)
    parse_tree = parse.parse(tokens, ctx)
    parse_tree.build_ancestry()
    collector.collect_names(parse_tree)

  regexes = [re.compile(pattern) for pattern in [
      r"[A-Z][A-Z0-9_]+",  # upper snake-case
      r"[a-z][a-z0-9_]+",  # lower snake-case
      r"_[A-Z0-9_]+",  # upper snake-case with underscore prefix
      r"_[a-z0-9_]+",  # lower snake-case with underscore prefix
  ]]

  outmap = {}
  patmap = {}
  for scope, varname in sorted(collector.varnames):
    if scope not in outmap:
      outmap[scope] = {}

    if scope not in patmap:
      patmap[scope] = {}
      for regex in regexes:
        patmap[scope][str(regex)] = 0
      patmap[scope]["other"] = 0

    for regex in regexes:
      if regex.match(varname):
        patmap[scope][str(regex)] += 1
        break
    else:
      patmap[scope]["other"] += 1

    if varname not in outmap[scope]:
      outmap[scope][varname] = 0
    outmap[scope][varname] += 1

  for scope, countmap in sorted(outmap.items()):
    outfile.write("\n{}\n{}\n".format(scope.name, "=" * len(scope.name)))
    for varname, count in sorted(countmap.items()):
      outfile.write("{}: {}\n".format(varname, count))

  for scope, countmap in sorted(patmap.items()):
    outfile.write("\n{}\n{}\n".format(scope.name, "=" * len(scope.name)))
    for varname, count in sorted(countmap.items()):
      outfile.write("{}: {}\n".format(varname, count))

  outfile.close()
  return returncode


def main():
  try:
    return inner_main()
  except SystemExit:
    return 0
  except common.UserError as ex:
    logger.fatal(ex.msg)
    return 1
  except common.InternalError as ex:
    logger.exception(ex.msg)
    return 2
  except AssertionError as ex:
    logger.exception(
        "An internal error occured. Please consider filing a bug report at "
        "github.com/cheshirekow/cmake_format/issues")
    return 2
  except:  # pylint: disable=bare-except
    logger.exception(
        "An internal error occured. Please consider filing a bug report at "
        "github.com/cheshirekow/cmake_format/issues")
    return 2


if __name__ == "__main__":
  sys.exit(main())
