# -*- coding: utf-8 -*-
"""
Check cmake listfile for lint
"""

import argparse
import io
import logging
import os
import sys

import cmake_format
from cmake_format import __main__
from cmake_format import configuration
from cmake_format import lexer
from cmake_format import parse
from cmake_format import parse_funs

from cmake_lint import basic_checker
from cmake_lint import lint_util

logger = logging.getLogger(__name__)


def process_file(config, local_ctx, infile_content):
  """
  Parse the input cmake file, re-format it, and print to the output file.
  """

  if config.line_ending == 'auto':
    detected = __main__.detect_line_endings(infile_content)
    config = config.clone()
    config.set_line_ending(detected)

  basic_checker.check_basics(config, local_ctx, infile_content)
  tokens = lexer.tokenize(infile_content)
  config.first_token = lexer.get_first_non_whitespace_token(tokens)
  parse_db = parse_funs.get_parse_db()
  parse_db.update(parse_funs.get_legacy_parse(config.fn_spec).kwargs)
  ctx = parse.ParseContext(parse_db, local_ctx)
  parse_tree = parse.parse(tokens, ctx)
  parse_tree.build_ancestry()
  basic_checker.check_tree(config, local_ctx, parse_tree)


def setup_argparse(argparser):
  argparser.add_argument('-v', '--version', action='version',
                         version=cmake_format.VERSION)
  argparser.add_argument(
      '-l', '--log-level', default="info",
      choices=["error", "warning", "info", "debug"])

  mutex = argparser.add_mutually_exclusive_group()
  mutex.add_argument('--dump-config', choices=['yaml', 'json', 'python'],
                     default=None, const='python', nargs='?',
                     help='If specified, print the default configuration to '
                          'stdout and exit')
  mutex.add_argument('-o', '--outfile-path', default=None,
                     help='Write errors to this file. '
                          'Default is stdout.')

  argparser.add_argument(
      '-c', '--config-files', nargs='+',
      help='path to configuration file(s)')
  argparser.add_argument('infilepaths', nargs='*')
  __main__.add_config_options(argparser)


USAGE_STRING = """
cmake-lint [-h]
           [--dump-config {yaml,json,python} | -o OUTFILE_PATH]
           [-c CONFIG_FILE]
           infilepath [infilepath ...]
"""


def main():
  """Parse arguments, open files, start work."""

  argparser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      usage=USAGE_STRING)

  setup_argparse(argparser)
  args = argparser.parse_args()
  logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

  if args.dump_config:
    config_dict = __main__.get_config(os.getcwd(), args.config_files)
    __main__.dump_config(args, config_dict, sys.stdout)
    sys.exit(0)

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

  global_ctx = lint_util.GlobalContext(outfile)
  returncode = 0
  for infile_path in args.infilepaths:
    # NOTE(josh): have to load config once for every file, because we may pick
    # up a new config file location for each path
    if infile_path == '-':
      config_dict = __main__.get_config(os.getcwd(), args.config_files)
    else:
      config_dict = __main__.get_config(infile_path, args.config_files)

    for key, value in vars(args).items():
      if (key in configuration.Configuration.get_field_names()
          and value is not None):
        config_dict[key] = value

    cfg = configuration.Configuration(**config_dict)
    if infile_path == '-':
      infile_path = os.dup(sys.stdin.fileno())

    try:
      infile = io.open(
          infile_path, mode='r', encoding=cfg.input_encoding, newline='')
    except (IOError, OSError):
      logger.error("Failed to open %s for read", infile_path)
      returncode = 1

    try:
      with infile:
        intext = infile.read()
    except UnicodeDecodeError:
      logger.error("Unable to read %s as %s", infile_path, cfg.input_encoding)

    try:
      local_ctx = global_ctx.get_file_ctx(infile_path, cfg)
      process_file(cfg, local_ctx, intext)
      outfile.write("{}\n{}\n".format(infile_path, "=" * len(infile_path)))
      local_ctx.writeout(outfile)
      outfile.write("\n")
      if local_ctx.has_lint():
        returncode = 1
    except:
      logger.warning('While processing %s', infile_path)
      raise
  global_ctx.write_summary(outfile)

  outfile.close()
  return returncode


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
  sys.exit(main())
