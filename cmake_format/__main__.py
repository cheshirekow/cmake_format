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
import json
import os
import pprint
import shutil
import sys
import tempfile

from cmake_format import formatter
from cmake_format import lexer
from cmake_format import parser


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
                     '.cmake-format.yaml',
                     '.cmake-format.json',
                     '.cmake-format.py'
                     'cmake-format.yaml',
                     'cmake-format.json',
                     'cmake-format.py']:
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
    with open(configfile_path, 'r') as config_file:
      return json.load(config_file)
  except:  # pylint: disable=bare-except
    pass

  try:
    import yaml
    with open(configfile_path, 'r') as config_file:
      return yaml.load(config_file)
  except:  # pylint: disable=bare-except
    pass

  try:
    config_dict = {}
    with open(configfile_path) as infile:
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
    with open(configfile_path, 'r') as config_file:
      if configfile_path.endswith('.json'):
        config_dict = json.load(config_file)
      elif configfile_path.endswith('.yaml'):
        import yaml
        config_dict = yaml.load(config_file)
      elif configfile_path.endswith('.py'):
        config_dict = {}
        with open(configfile_path) as infile:
          # pylint: disable=exec-used
          exec(infile.read(), config_dict)
      else:
        try_get_configdict(configfile_path)

  return config_dict


def dump_config(outfmt, outfile):
  """
  Dump the default configuration to stdout
  """

  config = formatter.Configuration()
  if outfmt == 'yaml':
    import yaml
    yaml.dump(config.as_dict(), sys.stdout, indent=2,
              default_flow_style=False)
    return
  elif outfmt == 'json':
    json.dump(config.as_dict(), sys.stdout, indent=2)
    sys.stdout.write('\n')
    return

  ppr = pprint.PrettyPrinter(indent=2)
  for key in config.get_field_names():
    value = formatter.serialize(getattr(config, key))
    outfile.write('{} = {}\n'.format(key, ppr.pformat(value)))


USAGE_STRING = """
cmake-format [-h]
             [--dump-config {yaml,json,python} | -i | -o OUTFILE_PATH]
             [-c CONFIG_FILE]
             infilepath [infilepath ...]
"""


def main():
  """Parse arguments, open files, start work."""

  arg_parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      usage=USAGE_STRING)

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

  for key, value in formatter.Configuration().as_dict().iteritems():
    flag = '--{}'.format(key.replace('_', '-'))
    optgroup.add_argument(flag, type=type(value), default=value)

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
    config_dict.update(vars(args))
    config = formatter.Configuration(**config_dict)
    if args.in_place:
      outfile = tempfile.NamedTemporaryFile(delete=False)
    else:
      if args.outfile_path == '-':
        outfile = sys.stdout
      else:
        outfile = open(args.outfile_path, 'w')

    parse_ok = True
    try:
      with open(infile_path, 'r') as infile:
        try:
          process_file(config, infile, outfile)
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
          shutil.move(outfile.name, infile_path)
      else:
        if args.outfile_path != '-':
          outfile.close()

  return 0


if __name__ == '__main__':
  sys.exit(main())
