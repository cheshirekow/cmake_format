"""
Parse cmake listfiles and format them nicely.

Formatting is configurable by providing a configuration file. The configuration
file can be in json, yaml, or python format. If no configuration file is
specified on the command line, cmake-format will attempt to find a suitable
configuration for each ``inputpath`` by checking recursively checking it's
parent directory up to the root of the filesystem. It will return the first
file it finds with a filename that matches '\\.?cmake-format(.yaml|.json|.py)'.

cmake-format can spit out the default configuration for you as starting point
for customization. Run with `--dump-config [yaml|cmake|python]`.
"""

import argparse
import io
import json
import logging
import os
import pprint
import shutil
import sys
import tempfile
import textwrap

from cmake_format import configuration
from cmake_format import formatter
from cmake_format import lexer
from cmake_format import parser

VERSION = '0.3.4'


def process_file(config, infile, outfile):
  """
  Parse the input cmake file, re-format it, and print to the output file.
  """

  pretty_printer = formatter.TreePrinter(config, outfile)
  tokens = lexer.tokenize(infile.read())
  tok_seqs = parser.digest_tokens(tokens)
  fst = parser.construct_fst(tok_seqs)
  pretty_printer.print_node(fst)


def find_config_file(infile_path):
  """
  Search parent directories of an infile path and find a config file if
  one exists.
  """
  realpath = os.path.realpath(infile_path)
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
    import yaml
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      return yaml.load(config_file)
  except:  # pylint: disable=bare-except
    pass

  try:
    config_dict = {}
    with io.open(configfile_path, 'r', encoding='utf-8') as infile:
      # pylint: disable=exec-used
      exec(infile.read(), config_dict)
    return config_dict
  except:  # pylint: disable=bare-except
    pass

  raise RuntimeError("Failed to parse {} as any of yaml, json, or python"
                     .format(configfile_path))


def get_config(infile_path, configfile_path):
  """
  If configfile_path is not none, then load the configuration. Otherwise search
  for a config file in the ancestry of the filesystem of infile_path and find
  a config file to load.
  """
  if configfile_path is None:
    configfile_path = find_config_file(infile_path)

  config_dict = {}
  if configfile_path:
    with io.open(configfile_path, 'r', encoding='utf-8') as config_file:
      if configfile_path.endswith('.json'):
        config_dict = json.load(config_file)
      elif configfile_path.endswith('.yaml'):
        import yaml
        config_dict = yaml.load(config_file)
      elif configfile_path.endswith('.py'):
        config_dict = {}
        with io.open(configfile_path, 'r', encoding='utf-8') as infile:
          # pylint: disable=exec-used
          exec(infile.read(), config_dict)
      else:
        try_get_configdict(configfile_path)

  return config_dict


def dump_config(outfmt, outfile):
  """
  Dump the default configuration to stdout
  """

  cfg = configuration.Configuration()
  if outfmt == 'yaml':
    import yaml
    yaml.dump(cfg.as_dict(), sys.stdout, indent=2,
              default_flow_style=False)
    return
  elif outfmt == 'json':
    json.dump(cfg.as_dict(), sys.stdout, indent=2)
    sys.stdout.write('\n')
    return

  ppr = pprint.PrettyPrinter(indent=2)
  for key in cfg.get_field_names():
    helptext = configuration.VARDOCS.get(key, None)
    if helptext:
      for line in textwrap.wrap(helptext, 78):
        outfile.write('# ' + line + '\n')
    value = getattr(cfg, key)
    if isinstance(value, dict):
      outfile.write('{} = {}\n\n'.format(key, json.dumps(value, indent=2)))
    else:
      outfile.write('{} = {}\n\n'.format(key, ppr.pformat(value)))


USAGE_STRING = """
cmake-format [-h]
             [--dump-config {yaml,json,python} | -i | -o OUTFILE_PATH]
             [-c CONFIG_FILE]
             infilepath [infilepath ...]
"""


def main():
  """Parse arguments, open files, start work."""
  # pylint: disable=too-many-statements

  # set up main logger, which logs everything. We'll leave this one logging
  # to the console
  format_str = '[%(levelname)-4s] %(filename)s:%(lineno)-3s: %(message)s'
  logging.basicConfig(level=logging.INFO,
                      format=format_str,
                      datefmt='%Y-%m-%d %H:%M:%S',
                      filemode='w')

  arg_parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      usage=USAGE_STRING)

  arg_parser.add_argument('-v', '--version', action='version',
                          version=VERSION)

  mutex = arg_parser.add_mutually_exclusive_group()
  mutex.add_argument('--dump-config', choices=['yaml', 'json', 'python'],
                     help='If specified, print the default configuration to '
                          'stdout and exit')
  mutex.add_argument('-i', '--in-place', action='store_true')
  mutex.add_argument('-o', '--outfile-path', default=None,
                     help='Where to write the formatted file. '
                          'Default is stdout.')
  arg_parser.add_argument('-c', '--config-file',
                          help='path to configuration file')
  arg_parser.add_argument('infilepaths', nargs='*')

  optgroup = arg_parser.add_argument_group(
      title='Formatter Configuration',
      description='Override configfile options')

  default_config = configuration.Configuration().as_dict()
  if sys.version_info[0] >= 3:
    value_types = (str, int, float)
  else:
    value_types = (str, unicode, int, float)

  for key in configuration.Configuration.get_field_names():
    value = default_config[key]
    helptext = configuration.VARDOCS.get(key, None)
    # NOTE(josh): argparse store_true isn't what we want here because we want
    # to distinguish between "not specified" = "default" and "specified"
    if key == 'additional_commands':
      continue
    elif isinstance(value, bool):
      optgroup.add_argument('--' + key.replace('_', '-'), nargs='?',
                            default=None, const=True,
                            type=configuration.parse_bool, help=helptext)
    elif isinstance(value, value_types) or value is None:
      optgroup.add_argument('--' + key.replace('_', '-'), type=type(value),
                            help=helptext,
                            choices=configuration.VARCHOICES.get(key, None))
    # NOTE(josh): argparse behavior is that if the flag is not specified on
    # the command line the value will be None, whereas if it's specified with
    # no arguments then the value will be an empty list. This exactly what we
    # want since we can ignore `None` values.
    elif isinstance(value, (list, tuple)):
      optgroup.add_argument('--' + key.replace('_', '-'), nargs='*',
                            help=helptext)
  args = arg_parser.parse_args()

  if args.dump_config:
    dump_config(args.dump_config, sys.stdout)
    sys.exit(0)

  assert args.in_place is False or args.outfile_path is None, \
      "if inplace is specified than outfile is invalid"
  assert (len(args.infilepaths) == 1
          or (args.in_place is True or args.outfile_path == '-')), \
      ("if more than one input file is specified, then formatting must be done"
       " in-place or written to stdout")
  if args.outfile_path is None:
    args.outfile_path = '-'

  for infile_path in args.infilepaths:
    config_dict = get_config(infile_path, args.config_file)
    for key, value in vars(args).items():
      if (key in configuration.Configuration.get_field_names()
          # pylint: disable=bad-continuation
              and value is not None):
        config_dict[key] = value

    cfg = configuration.Configuration(**config_dict)
    if args.in_place:
      ofd, tempfile_path = tempfile.mkstemp(suffix='.txt', prefix='CMakeLists-')
      os.close(ofd)
      outfile = io.open(tempfile_path, 'w', encoding='utf-8', newline='')
    else:
      if args.outfile_path == '-':
        # NOTE(josh): The behavior or sys.stdout is different in python2 and
        # python3. sys.stdout is opened in 'w' mode which means that write()
        # takes strings in python2 and python3 and, in particular, in python3
        # it does not take byte arrays. io.StreamWriter will write to
        # it with byte arrays (assuming it was opened with 'wb'). So we use
        # io.open instead of io.open in this case
        outfile = io.open(sys.stdout.fileno(), mode='w', encoding='utf-8',
                          newline='')
      else:
        outfile = io.open(args.outfile_path, 'w', encoding='utf-8',
                          newline='')

    parse_ok = True
    try:
      with io.open(infile_path, 'r', encoding='utf-8') as infile:
        try:
          process_file(cfg, infile, outfile)
        except:
          sys.stderr.write('Error while processing {}\n'.format(infile_path))
          raise

    except:
      parse_ok = False
      sys.stderr.write('While processing {}\n'.format(infile_path))
      raise
    finally:
      if args.in_place:
        outfile.close()
        if parse_ok:
          shutil.move(tempfile_path, infile_path)
      else:
        if args.outfile_path == '-':
          outfile.flush()
        else:
          outfile.close()

  return 0


if __name__ == '__main__':
  sys.exit(main())
