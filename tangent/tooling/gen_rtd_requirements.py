"""
Generate the rtd-requirements.txt file given a release tag and version number
"""

import argparse
import io
import os
import sys


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--tag", required=True)
  parser.add_argument("--version", required=True)
  parser.add_argument("-o", "--outfile-path", default="-")
  parser.add_argument("template")

  args = parser.parse_args()
  if args.tag == "from-travis":
    args.tag = os.environ["TRAVIS_TAG"]

  if args.outfile_path == "-":
    args.outfile_path = os.dup(sys.stdout.fileno())

  outfile = io.open(args.outfile_path, "w", encoding="utf-8")
  with io.open(args.template, "r", encoding="utf-8") as infile:
    template = infile.read()
  content = template.format(_tag=args.tag, _version=args.version)
  outfile.write(content)


if __name__ == "__main__":
  main()
