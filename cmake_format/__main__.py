"""Parse cmake listfiles and format them nicely."""

import argparse
import os
import json
import shutil
import sys
import tempfile

import yaml

from cmake_format import commands
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
                     'cmake-format.yaml',
                     'cmake-format.json']:
      configpath = os.path.join(head, filename)
      if os.path.exists(configpath):
        return configpath
    head2, _ = os.path.split(head)
    if head == head2:
      break
    head = head2
  return None


def get_config(infile_path, configfile_path):
  """
  If configfile_path is not none, then load the configuration. Otherwise search
  for a config file in the ancestry of the filesystem of infile_path and find
  a config file to load.
  """
  if configfile_path is None:
    configfile_path = find_config_file(infile_path)

  config = formatter.Configuration()
  if configfile_path:
    with open(configfile_path, 'r') as config_file:
      if configfile_path.endswith('.json'):
        config_dict = json.load(config_file)
      else:
        config_dict = yaml.load(config_file)
    config.merge(config_dict)
    for command_name, spec in config_dict.get('additional_commands',
                                              {}).iteritems():
      commands.decl_command(config.fn_spec, command_name, **spec)
  return config


def main():
  """Parse arguments, open files, start work."""

  arg_parser = argparse.ArgumentParser(description=__doc__)
  mutex = arg_parser.add_mutually_exclusive_group()
  mutex.add_argument('-i', '--in-place', action='store_true')
  mutex.add_argument('-o', '--outfile-path', default=None,
                     help='Where to write the formatted file. '
                          'Default is stdout.')
  arg_parser.add_argument('-c', '--config-file',
                          help='path to yaml config')
  arg_parser.add_argument('infilepaths', nargs='+')
  args = arg_parser.parse_args()

  assert args.in_place is False or args.outfile_path is None, \
      "if inplace is specified than outfile is invalid"
  assert (len(args.infilepaths) == 1
          or (args.in_place is True or args.outfile_path == '-')), \
      ("if more than one input file is specified, then formatting must be done"
       " in-place or written to stdout")
  if args.outfile_path is None:
    args.outfile_path = '-'

  for infile_path in args.infilepaths:
    config = get_config(infile_path, args.config_file)
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


if __name__ == '__main__':
  main()
