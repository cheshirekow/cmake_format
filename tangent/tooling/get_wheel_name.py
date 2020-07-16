"""
Get the wheel filename without building the wheel.
"""
from __future__ import print_function

import argparse
import io

from setuptools import Extension
from setuptools.dist import Distribution


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--name", required=True)
  parser.add_argument("--version-from", required=True)
  parser.add_argument("--has-extension-module", action="store_true")
  args = parser.parse_args()

  version = None
  with io.open(args.version_from, "r", encoding="utf-8") as infile:
    for line in infile:
      line = line.strip()
      if line.startswith("VERSION = "):
        version = line.split("=", 1)[1].strip().strip("'\"")

  if version is None:
    raise ValueError(
        "File {} does not container a 'VERSION = '"
        .format(args.version_from))

  attrs = {
      "name": args.name,
      "version": version
  }

  if args.has_extension_module:
    attrs["ext_modules"] = [
        Extension("__dummy", ["dummy.c"])
    ]

  dist = Distribution(attrs=attrs)
  bdist_wheel_cmd = dist.get_command_obj('bdist_wheel')
  bdist_wheel_cmd.ensure_finalized()
  distname = bdist_wheel_cmd.wheel_dist_name
  tag = '-'.join(bdist_wheel_cmd.get_tag())

  print("{}-{}.whl".format(distname, tag))


if __name__ == "__main__":
  main()
