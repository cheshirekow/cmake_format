"""
Get the version string by parsing a C++ header file. The version is expected
to be in the form of:

#define FOO_VERSION \
  { 0, 1, 0, "dev", 0 }
"""

from __future__ import unicode_literals

import argparse
import os
import io
import sys

OUTFILE_TPL = """
set({macro} "{semver}")
set({prefix}_API_VERSION "{api_version}")
set({prefix}_SO_VERSION "{so_version}")
"""


def main():
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("-o", "--outfilepath", default="-")
  argparser.add_argument("macro")
  argparser.add_argument("filepath")
  args = argparser.parse_args()
  if args.outfilepath == "-":
    args.outfilepath = os.dup(sys.stdout.fileno())

  version = None
  with io.open(args.filepath, "r", encoding="utf-8") as infile:
    lineiter = iter(infile)
    for line in lineiter:
      if line.startswith("#define " + args.macro):
        version = next(lineiter)
        break

  if version is None:
    return 1
  # Strip whitespace and brackets:
  version = version.strip()[1:-1]
  # Split along commas
  verparts = [part.strip().strip('"') for part in version.split(",")]

  prefix = args.macro
  if not prefix.endswith("_VERSION"):
    return 1

  prefix = prefix[:-len("_VERSION")]
  outputs = {
      "macro": args.macro,
      "prefix": prefix,
      "so_version": ".".join(verparts[:2]),
      "api_version": ".".join(verparts[:3]),
  }

  semver = ".".join(verparts[:3])
  pre_release = "".join(verparts[3:])
  if pre_release:
    semver += "-" + pre_release
  outputs["semver"] = semver

  with io.open(args.outfilepath, "w", encoding="utf-8") as outfile:
    outfile.write(OUTFILE_TPL.format(**outputs))
  return 0


if __name__ == "__main__":
  sys.exit(main())
