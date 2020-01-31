"""
Generate the rtd-requirements.txt file given a release tag and version number
"""

import argparse
import io
import os
import sys

TEMPLATE = "\n".join([
    ("https://github.com/cheshirekow/cmake_format/releases/download/"
     "{_tag}/cmake_format-{_version}-py3-none-any.whl"),
    "PyYAML==5.3"
]) + "\n"


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("tag")
  parser.add_argument("version")
  parser.add_argument("-o", "--outfile-path", default="-")

  args = parser.parse_args()
  if args.outfile_path == "-":
    args.outfile_path = os.dup(sys.stdout.fileno())

  outfile = io.open(args.outfile_path, "w", encoding="utf-8")
  content = TEMPLATE.format(_tag=args.tag, _version=args.version)
  outfile.write(content)


if __name__ == "__main__":
  main()
