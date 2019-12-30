"""
Bump cmake version number
"""

import argparse
import collections
import io
import logging
import json
import os
import re
import sys

logger = logging.getLogger(__name__)


def stringify(version):
  """Given a version as a list/tuple of integers, return a list of strings
     coresponding to the different semantic version components."""
  version = list(str(x) for x in version)
  if len(version) > 3:
    version[3] = "dev" + version[3]
  return version


def format_pip_vstring(version):
  """Format the version items as a pip version string."""
  return ".".join(stringify(version))


def format_semver(version):
  """Format the version items as a semver."""
  version = stringify(version)
  left_part = ".".join(version[:3])
  right_part = ".".join(version[3:])
  parts = [left_part]
  if right_part:
    parts.append(right_part)
  return "-".join(parts)


INIT_VERSION_PATTERN = r"VERSION = '(\d+)\.(\d+)\.(\d+)(?:\.dev(\d+))'"


def get_current_version(filepath):
  """
  Process the __init__.py which is the canonical version number source.
  Return the current version as a list of integers.
  """
  pattern = re.compile(INIT_VERSION_PATTERN)
  with io.open(filepath, "r", encoding="utf-8") as infile:
    for line in infile:
      match = pattern.match(line.strip())
      if match:
        return [int(x) for x in match.groups()]
  raise RuntimeError("Failed to find the current version in __init__.py")


def process_init(filepath, version):
  """
  Process the __init__.py which is the canonical version number source.
  Increment the desired semver index by one. Write out the new __init__.py
  and return the semver tuple.
  """
  pattern = re.compile(INIT_VERSION_PATTERN)
  outpath = filepath + ".tmp"
  with io.open(filepath, "r", encoding="utf-8") as infile:
    with io.open(outpath, "w", encoding="utf-8") as outfile:
      for line in infile:
        match = pattern.match(line.strip())
        if match:
          line = "VERSION = '{}'\n".format(format_pip_vstring(version))
        outfile.write(line)
  os.rename(outpath, filepath)
  return version


def process_installation_rst(filepath, version):
  """
  Process doc/installation.rst which uses the version number in some examples
  """
  pattern = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
  repl = "v{0}.{1}.{2}".format(*version[:3])
  outpath = filepath + ".tmp"

  with io.open(filepath, "r", encoding="utf-8") as infile:
    with io.open(outpath, "w", encoding="utf-8") as outfile:
      for line in infile:
        line = pattern.sub(repl, line)
        outfile.write(line)
  os.rename(outpath, filepath)


def process_json(filepath, version):
  """
  Process the vscode extension package.json and package-lock.json files
  """
  with io.open(filepath, "r", encoding="utf-8") as infile:
    data = json.load(infile, object_pairs_hook=collections.OrderedDict)
  data["version"] = format_semver(version)
  with io.open(filepath, "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, indent=4)
    outfile.write("\n")


def main():
  fields = ["major", "minor", "patch", "dev", "drop-dev"]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("field", nargs="?", choices=fields, default="dev")
  args = parser.parse_args()

  thisdir = os.path.dirname(os.path.realpath(__file__))
  rootdir = os.path.dirname(os.path.dirname(thisdir))
  init_path = os.path.join(rootdir, "cmake_format/__init__.py")
  current_version = get_current_version(init_path)

  if args.field == "drop-dev":
    new_version = current_version[:3]
  else:
    field_idx = fields.index(args.field)
    new_version = list(current_version)
    new_version[field_idx] += 1

  process_init(init_path, new_version)
  process_installation_rst(
      os.path.join(rootdir, "cmake_format/doc/installation.rst"), new_version)
  process_json(
      os.path.join(rootdir, "cmake_format/vscode_extension/package.json"),
      new_version)
  process_json(
      os.path.join(rootdir, "cmake_format/vscode_extension/package-lock.json"),
      new_version)
  return 0


if __name__ == "__main__":
  sys.exit(main())
