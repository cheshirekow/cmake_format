# -*- coding: utf-8 -*-
"""
Parse cmake listfiles and format them nicely.

Formatting is configurable by providing a configuration file. The configuration
file can be in json, yaml, or python format. If no configuration file is
specified on the command line, cmake-format will attempt to find a suitable
configuration for each ``inputpath`` by checking recursively checking it's
parent directory up to the root of the filesystem. It will return the first
file it finds with a filename that matches '\\.?cmake-format(.yaml|.json|.py)'.

cmake-format can spit out the default configuration for you as starting point
for customization. Run with `--dump-config [yaml|json|python]`.
"""
from __future__ import unicode_literals

import argparse
import collections
try:
  from collections.abc import Mapping
except ImportError:
  from collections import Mapping
import io
import json
import logging
import os
import shutil
import sys

import cmake_format
from cmake_format import commands
from cmake_format import configuration
from cmake_format import config_util
from cmake_format import formatter
from cmake_format import lexer
from cmake_format import markup
from cmake_format import parse
from cmake_format import parse_funs
from cmake_format.parse.common import NodeType, TreeNode
from cmake_format.parse.printer import dump_tree as dump_parse


logger = logging.getLogger(__name__)


def detect_line_endings(infile_content):
  windows_count = infile_content.count('\r\n')
  unix_count = infile_content.count('\n') - windows_count
  if windows_count > unix_count:
    return 'windows'

  return 'unix'


def dump_markup(nodes, config, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes. Takes as input a full
  parse tree.
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for idx, node in enumerate(nodes):
    if not isinstance(node, TreeNode):
      continue

    # outfile.write(indent)
    # if idx + 1 == len(nodes):
    #   outfile.write('└─ ')
    # else:
    #   outfile.write('├─ ')

    noderep = repr(node)
    if sys.version_info[0] < 3:
      noderep = getattr(noderep, 'decode')('utf-8')

    if node.node_type is NodeType.COMMENT:
      outfile.write(noderep)
      outfile.write('\n')
      inlines = []
      for token in node.children:
        assert isinstance(token, lexer.Token)
        if token.type == lexer.TokenType.COMMENT:
          inlines.append(token.spelling.strip().lstrip('#'))
      items = markup.parse(inlines, config)
      for item in items:
        outfile.write("{}\n".format(item))
      outfile.write("\n")

    if not hasattr(node, 'children'):
      continue

    if idx + 1 == len(nodes):
      dump_markup(node.children, config, outfile, indent + '    ')
    else:
      dump_markup(node.children, config, outfile, indent + '│   ')


def process_file(config, infile_content, dump=None):
  """
  Parse the input cmake file, re-format it, and print to the output file.
  """

  outfile = io.StringIO(newline='')
  if config.line_ending == 'auto':
    detected = detect_line_endings(infile_content)
    config = config.clone()
    config.set_line_ending(detected)
  tokens = lexer.tokenize(infile_content)
  if dump == "lex":
    for token in tokens:
      outfile.write("{}\n".format(token))
    return outfile.getvalue(), True
  config.first_token = lexer.get_first_non_whitespace_token(tokens)
  parse_db = parse_funs.get_parse_db()
  parse_db.update(parse_funs.get_legacy_parse(config.fn_spec).kwargs)
  ctx = parse.ParseContext(parse_db)
  parse_tree = parse.parse(tokens, ctx)
  if dump == "parse":
    dump_parse([parse_tree], outfile)
    return outfile.getvalue(), True
  if dump == "markup":
    dump_markup([parse_tree], config, outfile)
    return outfile.getvalue(), True

  box_tree = formatter.layout_tree(parse_tree, config)
  if dump == "layout":
    formatter.dump_tree([box_tree], outfile)
    return outfile.getvalue(), True

  outstr = formatter.write_tree(box_tree, config, infile_content)
  if config.emit_byteorder_mark:
    outstr = "\ufeff" + outstr

  return (outstr, box_tree.reflow_valid)


def find_config_file(infile_path):
  """
  Search parent directories of an infile path and find a config file if
  one exists.
  """
  realpath = os.path.realpath(infile_path)
  if os.path.isdir(infile_path):
    head = infile_path
  else:
    head, _ = os.path.split(realpath)

  while head:
    for filename in ['.cmake-format',
                     '.cmake-format.py',
                     '.cmake-format.json',
                     '.cmake-format.yaml',
                     'cmake-format.py',
                     'cmake-format.json',
                     'cmake-format.yaml', ]:
      configpath = os.path.join(head, filename)
      if os.path.exists(configpath):
        return configpath
    head2, _ = os.path.split(head)
    if head == head2:
      break
    head = head2
  return None


def load_yaml(config_file):
  """
  Attempt to load yaml configuration from an opened file
  """
  import yaml
  try:
    from yaml import CLoader as Loader
  except ImportError:
    from yaml import Loader
  out = yaml.load(config_file, Loader=Loader)
  if out is None:
    return {}
  return out


def exec_pyconfig(configfile_path):
  _global = config_util.ExecGlobal(configfile_path)
  with io.open(configfile_path, 'r', encoding='utf-8') as infile:
    # pylint: disable=exec-used
    exec(infile.read(), _global)
  return _global


def try_get_configdict(configfile_path):
  """
  Try to read the configuration as yaml first, then json, then python.

  TODO(josh): maybe read the first line and look for some kind of comment
  sentinel to indicate the file format?
  """
  try:
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      return json.load(config_file)
  except:  # pylint: disable=bare-except
    pass

  try:
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      return load_yaml(config_file)
  except:  # pylint: disable=bare-except
    pass

  try:
    return exec_pyconfig(configfile_path)
  except:  # pylint: disable=bare-except
    pass

  raise RuntimeError("Failed to parse {} as any of yaml, json, or python"
                     .format(configfile_path))


def get_config_dict(configfile_path):
  """
  Return a dictionary of configuration options read from the given file path.
  If the filepath has a known extension then we parse it according to that
  extension. Otherwise we try to parse is using each parser one by one.
  """
  if configfile_path.endswith('.json'):
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      return json.load(config_file)

  if configfile_path.endswith('.yaml'):
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      return load_yaml(config_file)

  if configfile_path.endswith('.py'):
    return exec_pyconfig(configfile_path)

  return try_get_configdict(configfile_path)


def map_merge(output_map, increment_map):
  """
  Merge `increment_map` into `output_map` recursively.
  """
  for key, increment_value in increment_map.items():
    if key not in output_map:
      output_map[key] = increment_value
      continue

    existing_value = output_map[key]
    if isinstance(existing_value, Mapping):
      if isinstance(increment_value, Mapping):
        map_merge(existing_value, increment_value)
      else:
        logger.warning(
            "Cannot merge config %s of type %s into a dictionary",
            key, type(increment_value))
      continue

    output_map[key] = increment_value

  return output_map


def get_config(infile_path, configfile_paths):
  """
  If configfile_path is not none, then load the configuration. Otherwise search
  for a config file in the ancestry of the filesystem of infile_path and find
  a config file to load.
  """
  if configfile_paths is None:
    inferred_configpath = find_config_file(infile_path)
    if inferred_configpath is None:
      return {}
    configfile_paths = [inferred_configpath]

  config_dict = {}
  for configfile_path in configfile_paths:
    configfile_path = os.path.expanduser(configfile_path)
    increment_dict = get_config_dict(configfile_path)
    map_merge(config_dict, increment_dict)

  return config_dict


def yaml_odict_handler(dumper, value):
  """
  Represent ordered dictionaries as yaml maps.
  """
  return dumper.represent_mapping(u'tag:yaml.org,2002:map', value)


def yaml_register_odict(dumper):
  """
  Register an order dictionary handler with the given yaml dumper
  """
  dumper.add_representer(collections.OrderedDict, yaml_odict_handler)


def dump_config(args, config_dict, outfile):
  """
  Dump the default configuration to stdout
  """

  outfmt = args.dump_config

  for key, value in vars(args).items():
    if (key in configuration.Configuration.get_field_names()
        and value is not None):
      config_dict[key] = value

  cfg = configuration.Configuration(**config_dict)
  # Don't dump default per-command configs
  for key in commands.get_default_config():
    cfg.per_command.pop(key, None)

  if outfmt == 'yaml':
    import yaml
    yaml_register_odict(yaml.SafeDumper)
    yaml_register_odict(yaml.Dumper)
    yaml.dump(cfg.as_odict(), outfile, indent=2,
              default_flow_style=False, sort_keys=False)
    return
  if outfmt == 'json':
    json.dump(cfg.as_odict(), outfile, indent=2)
    outfile.write('\n')
    return

  cfg.dump(outfile)


USAGE_STRING = """
cmake-format [-h]
             [--dump-config {yaml,json,python} | -i | -o OUTFILE_PATH]
             [-c CONFIG_FILE]
             infilepath [infilepath ...]
"""


def add_config_options(arg_parser):
  """
  Add configuration options as flags to the argument parser
  """
  format_group = arg_parser.add_argument_group(
      title="Formatter Configuration",
      description="Override configfile options affecting general formatting")

  comment_group = arg_parser.add_argument_group(
      title="Comment Formatting",
      description="Override config options affecting comment formatting")

  misc_group = arg_parser.add_argument_group(
      title="Misc Options",
      description="Override miscellaneous config options")

  default_config = configuration.Configuration().as_dict()
  if sys.version_info[0] >= 3:
    value_types = (str, int, float)
  else:
    value_types = (str, unicode, int, float)

  for key in configuration.Configuration.get_field_names():
    if key in configuration.COMMENT_GROUP:
      optgroup = comment_group
    elif key in configuration.MISC_GROUP:
      optgroup = misc_group
    else:
      optgroup = format_group

    value = default_config[key]
    helptext = configuration.VARDOCS.get(key, None)
    # NOTE(josh): argparse store_true isn't what we want here because we want
    # to distinguish between "not specified" = "default" and "specified"
    if key == 'additional_commands':
      continue
    elif isinstance(value, bool):
      optgroup.add_argument('--' + key.replace('_', '-'), nargs='?',
                            default=None, const=(not value),
                            type=config_util.parse_bool, help=helptext)
    elif isinstance(value, value_types):
      optgroup.add_argument('--' + key.replace('_', '-'), type=type(value),
                            help=helptext,
                            choices=configuration.VARCHOICES.get(key, None))
    elif value is None:
      # If the value is None then we can't really tell what it's supposed to
      # be. I guess let's assume string in this case.
      optgroup.add_argument('--' + key.replace('_', '-'), help=helptext,
                            choices=configuration.VARCHOICES.get(key, None))
    # NOTE(josh): argparse behavior is that if the flag is not specified on
    # the command line the value will be None, whereas if it's specified with
    # no arguments then the value will be an empty list. This exactly what we
    # want since we can ignore `None` values.
    elif isinstance(value, (list, tuple)):
      typearg = None
      if value:
        typearg = type(value[0])
      optgroup.add_argument('--' + key.replace('_', '-'), nargs='*',
                            type=typearg, help=helptext)


def setup_argparser(arg_parser):
  """
  Add argparse options to the parser.
  """
  arg_parser.add_argument('-v', '--version', action='version',
                          version=cmake_format.VERSION)
  arg_parser.add_argument(
      '-l', '--log-level', default="info",
      choices=["error", "warning", "info", "debug"])

  mutex = arg_parser.add_mutually_exclusive_group()
  mutex.add_argument('--dump-config', choices=['yaml', 'json', 'python'],
                     default=None, const='python', nargs='?',
                     help='If specified, print the default configuration to '
                          'stdout and exit')
  mutex.add_argument('--dump', choices=['lex', 'parse', 'layout', 'markup'],
                     default=None)

  mutex = arg_parser.add_mutually_exclusive_group()
  mutex.add_argument('-i', '--in-place', action='store_true')
  mutex.add_argument(
      '--check', action='store_true',
      help="Exit with status code 0 if formatting would not change file "
           "contents, or status code 1 if it would")
  mutex.add_argument('-o', '--outfile-path', default=None,
                     help='Where to write the formatted file. '
                          'Default is stdout.')

  arg_parser.add_argument(
      '-c', '--config-files', nargs='+',
      help='path to configuration file(s)')
  arg_parser.add_argument('infilepaths', nargs='*')
  add_config_options(arg_parser)


def main():
  """Parse arguments, open files, start work."""

  arg_parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      usage=USAGE_STRING)

  setup_argparser(arg_parser)
  args = arg_parser.parse_args()
  logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

  if args.dump_config:
    config_dict = get_config(os.getcwd(), args.config_files)
    dump_config(args, config_dict, sys.stdout)
    sys.exit(0)

  if args.dump_config or args.dump:
    assert not args.in_place, \
        ("-i/--in-place not allowed when dumping")

  assert args.in_place is False or args.outfile_path is None, \
      "if inplace is specified than outfile is invalid"
  assert (len(args.infilepaths) == 1
          or (args.in_place is True or args.outfile_path is None)), \
      ("if more than one input file is specified, then formatting must be done"
       " in-place or written to stdout")

  if args.outfile_path is None:
    args.outfile_path = '-'

  if '-' in args.infilepaths:
    assert len(args.infilepaths) == 1, \
        "You cannot mix stdin as an input with other input files"
    assert args.outfile_path == '-', \
        "If stdin is the input file, then stdout must be the output file"

  returncode = 0
  for infile_path in args.infilepaths:
    # NOTE(josh): have to load config once for every file, because we may pick
    # up a new config file location for each path
    if infile_path == '-':
      config_dict = get_config(os.getcwd(), args.config_files)
    else:
      config_dict = get_config(infile_path, args.config_files)

    for key, value in vars(args).items():
      if (key in configuration.Configuration.get_field_names()
          and value is not None):
        config_dict[key] = value

    cfg = configuration.Configuration(**config_dict)
    if infile_path == '-':
      infile = io.open(os.dup(sys.stdin.fileno()),
                       mode='r', encoding=cfg.input_encoding, newline='')
    else:
      infile = io.open(
          infile_path, 'r', encoding=cfg.input_encoding, newline='')
    with infile:
      intext = infile.read()

    try:
      outtext, reflow_valid = process_file(cfg, intext, args.dump)
      if cfg.require_valid_layout and not reflow_valid:
        logger.error("Failed to format %s", infile_path)
        returncode = 1
        continue
    except:
      logger.warning('While processing %s', infile_path)
      raise

    if args.check:
      if intext != outtext:
        returncode = 1
      continue

    if args.in_place:
      if intext == outtext:
        logger.debug("No delta for %s", infile_path)
        continue
      tempfile_path = infile_path + ".cmf-temp"
      outfile = io.open(tempfile_path, 'w', encoding=cfg.output_encoding,
                        newline='')
    else:
      if args.outfile_path == '-':
        # NOTE(josh): The behavior of sys.stdout is different in python2 and
        # python3. sys.stdout is opened in 'w' mode which means that write()
        # takes strings in python2 and python3 and, in particular, in python3
        # it does not take byte arrays. io.StreamWriter will write to
        # it with byte arrays (assuming it was opened with 'wb'). So we use
        # io.open instead of open in this case
        outfile = io.open(os.dup(sys.stdout.fileno()),
                          mode='w', encoding=cfg.output_encoding, newline='')
      else:
        outfile = io.open(args.outfile_path, 'w', encoding=cfg.output_encoding,
                          newline='')

    with outfile:
      outfile.write(outtext)

    if args.in_place:
      shutil.copymode(infile_path, tempfile_path)
      shutil.move(tempfile_path, infile_path)

  return returncode


if __name__ == '__main__':
  # set up main logger, which logs everything. We'll leave this one logging
  # to the console
  format_str = '%(levelname)-4s %(filename)s:%(lineno)-3s: %(message)s'
  logging.basicConfig(level=logging.INFO,
                      format=format_str,
                      filemode='w')

  sys.exit(main())
