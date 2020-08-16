"""
Generate configuration details docpage
"""

from __future__ import unicode_literals

import argparse
import io
import os
import pprint
import re
import sys
import tempfile

from cmakelang import configuration
from cmakelang import config_util


def parse_sourcefile(infile):
  ruler = re.compile(r"[=\-\^~]+")
  lines = infile.read().split("\n")

  out = {}
  stack = [out]
  sepmap = {
      "=": 0,
      "-": 1,
      "^": 2,
      "~": 3
  }

  varname = None
  buf = []

  lineiter = enumerate(lines)
  for idx, line in lineiter:
    if ruler.match(line):
      if lines[idx + 2] == line:
        # Section heading
        if varname:
          stack[-1][varname] = "\n".join(buf)
          varname = None
        buf = []

        title = lines[idx + 1]
        newdict = {}
        parent_idx = sepmap[line[0]]
        stack[parent_idx][title] = newdict
        stack = stack[:parent_idx + 1]
        stack.append(newdict)
        next(lineiter)
        next(lineiter)
    elif line and ruler.match(lines[idx + 1]):
      # Variable heading
      if varname:
        stack[-1][varname] = "\n".join(buf[:-1])
        varname = None
      buf = []
      varname = line
      next(lineiter)
    else:
      buf.append(line)

  if varname:
    stack[-1][varname] = "\n".join(buf[:-1])
    buf = []
    varname = None

  return out


SEPARATORS = ["=", "-", "^", "~"]


def get_command_line(descr):
  argparser = argparse.ArgumentParser(usage="")
  descr.add_to_argparse(argparser)
  sys.stdout.flush()
  stdout_copy = os.dup(sys.stdout.fileno())
  with tempfile.NamedTemporaryFile(delete=False) as outfile:
    tmppath = outfile.name
    os.dup2(outfile.fileno(), sys.stdout.fileno())
    try:
      argparser.parse_args(["--help"])
    except SystemExit:
      pass
  sys.stdout.flush()
  os.dup2(stdout_copy, sys.stdout.fileno())
  with io.open(tmppath, "r", encoding="utf-8") as infile:
    content = infile.read()
  os.unlink(tmppath)
  return "\n".join(content.split("\n")[4:])


ROOT_CONFIG = None


def get_config_example(root, obj, descr):
  default_value = descr.__get__(obj, None)
  descr.__set__(obj, default_value)
  buf = io.StringIO()
  root.dump(buf, with_defaults=False)
  descr.unset(obj)
  return buf.getvalue()


def write_outfile(outfile, data, obj, name=None, depth=0, root=None):
  if root is None:
    root = obj

  helptext = obj.__class__.__doc__.strip()
  title, helptext = (helptext + "\n").split("\n", 1)

  if not title and name:
    title = name

  outfile.write(SEPARATORS[depth] * len(title))
  outfile.write("\n")
  outfile.write(title)
  outfile.write("\n")
  outfile.write(SEPARATORS[depth] * len(title))
  outfile.write("\n\n")

  if helptext.strip():
    outfile.write("\n")
    outfile.write(helptext)

  ppr = pprint.PrettyPrinter(indent=2, width=72)
  for descr in obj._field_registry:  # pylint: disable=protected-access
    if isinstance(descr, config_util.SubtreeDescriptor):
      subobj = descr.__get__(obj, type(obj))
      write_outfile(
          outfile, data.get(descr.name, {}), subobj, descr.name, depth + 1,
          root)
    elif isinstance(descr, config_util.FieldDescriptor):
      outfile.write(".. _{}:\n\n".format(descr.name))
      outfile.write(descr.name)
      outfile.write("\n")
      outfile.write("=" * len(descr.name))
      outfile.write("\n\n")

      if descr.helptext:
        outfile.write(descr.helptext.strip())
        outfile.write("\n\n")

      heading = "default value:"
      outfile.write("{}\n{}\n\n".format(heading, "-" * len(heading)))
      outfile.write(".. code::\n\n")
      for line in ppr.pformat(descr.default_value).split("\n"):
        outfile.write("  {}\n".format(line))
      outfile.write("\n")

      if descr.name in data:
        heading = "detailed description:"
        outfile.write("{}\n{}\n\n".format(heading, "-" * len(heading)))
        outfile.write(data[descr.name].strip())
        outfile.write("\n\n")

      cmdline = get_command_line(descr)
      if cmdline:
        heading = "command-line option:"
        outfile.write("{}\n{}\n\n".format(heading, "-" * len(heading)))
        outfile.write(".. code:: \n\n")
        for line in cmdline.split("\n"):
          outfile.write("   {}\n".format(line))
        outfile.write("\n")

      config = get_config_example(root, obj, descr)
      if config:
        heading = "config-file entry:"
        outfile.write("{}\n{}\n\n".format(heading, "-" * len(heading)))
        outfile.write(".. code:: \n\n")
        for line in config.split("\n"):
          outfile.write("  {}\n".format(line))
        outfile.write("\n")

    else:
      raise RuntimeError("Field registry contains unknown descriptor")


def main():
  rootdir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-3])

  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument(
      "--sourcefile",
      default=os.path.join(rootdir, "cmakelang/doc/configopts.rst"))
  argparser.add_argument(
      "outfile", nargs="?", default="-")
  args = argparser.parse_args()

  with io.open(args.sourcefile, "r", encoding="utf-8") as infile:
    data = parse_sourcefile(infile)

  if args.outfile == "-":
    args.outfile = os.dup(sys.stdout.fileno())

  with io.open(args.outfile, "w", encoding="utf-8") as outfile:
    outfile.write(".. _configopts:\n\n")
    write_outfile(
        outfile, data["global"], configuration.Configuration(), "global")


if __name__ == "__main__":
  main()
