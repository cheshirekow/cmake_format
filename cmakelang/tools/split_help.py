"""
Split help contents into the tool-specific short help and the common
configuration options.
"""

import argparse
import io

from cmakelang import configuration


def main():
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("infile")
  argparser.add_argument("unique_outfile")
  argparser.add_argument("common_outfile", nargs="?", default="/dev/null")
  args = argparser.parse_args()

  matchlines = []
  for _, item in vars(configuration).items():
    if (isinstance(item, type) and
        issubclass(item, configuration.ConfigObject) and
        item is not configuration.ConfigObject):
      firstline = item.__doc__.strip().split("\n")[0]
      matchlines.append(firstline)

  unique_lines = []
  common_lines = []
  with io.open(args.infile, "r", encoding="utf-8") as infile:
    for line in infile:
      if line.strip().rstrip(":") in matchlines:
        common_lines.append(line)
        break
      unique_lines.append(line)

    for line in infile:
      common_lines.append(line)

  with io.open(args.unique_outfile, "w", encoding="utf-8") as outfile:
    outfile.write("".join(unique_lines))

  if args.common_outfile != "/dev/null":
    with io.open(args.common_outfile, "w", encoding="utf-8") as outfile:
      outfile.write("".join(common_lines))


if __name__ == "__main__":
  main()
