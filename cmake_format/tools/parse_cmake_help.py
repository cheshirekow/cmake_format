# PYTHON_ARGCOMPLETE_OK
"""
Parse cmake help to generate certain input files

TODO(josh): `cmake --help-module-list` to get a list of builtin find-modules
that we can search for more commands.
TODO(josh): `cmake --help-commandplist` to get a list of builtin commands
that we can generate parsers for.
"""

import argparse
import io
import logging
import os
import re
import subprocess
import sys

import jinja2

logger = logging.getLogger(__name__)


def get_abspath(relpath):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), relpath))


def make_pattern(namestr):
  """
  Look for any generic labels within a cmake property or variable name
  (e.g. `<LANG>` in `<LANG>_CPPLINT`) and convert the pattern string to a
  regular expression pattern (e.g. `.*_CPPLINT`)
  """
  return re.sub("<[^>]+>", ".*", namestr)


def get_properties(args, jenv):

  proc = subprocess.Popen(
      [args.cmake, "--help-property-list"],
      stdout=subprocess.PIPE)

  with proc.stdout as infile:
    properties = [line.decode("utf-8").strip() for line in infile]
  patterns = [make_pattern(namestr) for namestr in properties]
  proc.wait()

  template = jenv.get_template("properties.jinja.py")
  content = template.render(patterns=patterns)

  if args.outfile == "-":
    args.outfile = os.dup(sys.stdout.fileno())
  with io.open(args.outfile, "w", encoding="utf-8") as outfile:
    outfile.write(content)
    outfile.write("\n")


def get_variables(args, jenv):

  proc = subprocess.Popen(
      [args.cmake, "--help-variable-list"],
      stdout=subprocess.PIPE)

  with proc.stdout as infile:
    variables = [line.decode("utf-8").strip() for line in infile]
  patterns = [make_pattern(namestr) for namestr in variables]
  proc.wait()

  template = jenv.get_template("variables.jinja.py")
  content = template.render(patterns=patterns)

  if args.outfile == "-":
    args.outfile = os.dup(sys.stdout.fileno())
  with io.open(args.outfile, "w", encoding="utf-8") as outfile:
    outfile.write(content)
    outfile.write("\n")


def get_command_list(args):
  """
  Get a list of all the builtin cmake commands (statement names).
  """
  proc = subprocess.Popen(
      [args.cmake, "--help-command-list"],
      stdout=subprocess.PIPE)

  with proc.stdout as infile:
    return [line.decode("utf-8").strip() for line in infile]


def get_command_help(args, command_name):
  """
  Get the help string for a specific command
  """
  proc = subprocess.Popen(
      [args.cmake, "--help-command", command_name],
      stdout=subprocess.PIPE)
  with proc.stdout as infile:
    return infile.read().decode("utf-8")


def get_usages(helpstr):
  """
  Parse the command help string and return a list of command usage strings.
  """
  usage = []
  active = False

  buf = ""
  lineiter = iter(helpstr.split("\n"))
  for line in lineiter:
    if active:
      if not line.strip():
        active = False
        usage.append(buf)
        buf = ""
      else:
        buf += line.rstrip() + "\n"
    elif line.strip() == "::":
      next(lineiter, None)
      active = True

  if buf:
    usage.append(buf)
  return usage


def cmd_get_usages(args, jenv):
  for command_name in get_command_list(args):
    helpstr = get_command_help(args, command_name)
    for usage in get_usages(helpstr):
      print(usage)


def setup_argparse(parser):
  """Setup argument parser"""
  parser.add_argument(
      "--cmake", default="cmake",
      help="Cmake binary path or command. Default is `cmake`")
  parser.add_argument(
      "--outfile", default="-",
      help="output file, default is stdout")
  subparsers = parser.add_subparsers(dest="command")
  subparsers.add_parser("properties")
  subparsers.add_parser("variables")
  subparsers.add_parser("usages")


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  setup_argparse(parser)
  try:
    import argcomplete
    argcomplete.autocomplete(parser)
  except ImportError:
    pass
  args = parser.parse_args()

  thisdir = os.path.abspath(os.path.dirname(__file__))
  jenv = jinja2.Environment(
      loader=jinja2.FileSystemLoader(thisdir)
  )

  if args.command == "properties":
    get_properties(args, jenv)
  elif args.command == "variables":
    get_variables(args, jenv)
  elif args.command == "usages":
    cmd_get_usages(args, jenv)
  else:
    logger.warning("Unknown command %s", args.command)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()
