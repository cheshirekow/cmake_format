"""
Generate stubs for missing parsers
"""

import argparse
import io
import os
import subprocess
import sys

from cmakelang import parse

TEMPLATE = '''

def parse_{0}(ctx, tokens, breakstack):
  """
  ::

    {0}

  :see: https://cmake.org/cmake/help/latest/command/{0}.html
  """
'''


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("outfile", nargs="?", default="-")
  args = parser.parse_args()

  missing_commands = []
  proc = subprocess.Popen(
      ["cmake", "--help-command-list"],
      stdout=subprocess.PIPE)

  parse_db = parse.funs.get_parse_db()

  with proc.stdout as infile:
    for line in infile:
      command = line.strip().decode("utf-8")
      if command not in parse_db and not command.startswith("end"):
        missing_commands.append(command)
  proc.wait()

  outfile_path = args.outfile
  if outfile_path == "-":
    outfile_path = os.dup(sys.stdout.fileno())

  with io.open(outfile_path, "w", encoding="utf-8") as outfile:
    for command in missing_commands:
      outfile.write(TEMPLATE.format(command))

    outfile.write("\n\ndef populate_db(parse_db):\n")
    for command in missing_commands:
      outfile.write('  parse_db["{0}"] = parse_{0}\n'.format(command))


if __name__ == "__main__":
  main()
