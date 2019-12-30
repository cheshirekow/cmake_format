"""
Scan the source tree rooted at a particulary directory and build a list of all
lintable files. Compare that list against the list of names in any
`.lint-manifest` in the binary tree. If the two are not identical, exit with
nonzero status code.
"""

import argparse
import io
import os
import logging
import re
import sys

KNOWN_EXTENSIONS = [
    ".cmake",
    ".c",
    ".cc",
    ".cxx",
    ".cpp",
    ".h",
    ".hxx",
    ".hpp",
    ".js",
    ".py",
]


def has_known_extension(filename):
  for extension in KNOWN_EXTENSIONS:
    if filename.lower().endswith(extension):
      return True
  return False


SENTINEL_NAMES = [
    "CMakeLists.txt",
]


def is_sentinel_name(filename):
  return filename in SENTINEL_NAMES


REJECT_NAMES = [
    # Outputs of cmake in-source configure
    "CTestTestfile.cmake",
    "cmake_install.cmake",
]


def is_known_reject(filename):
  return filename in REJECT_NAMES


def get_source_manifest(rootdir, exclude_pattern):
  manifest = []
  excluded = []
  for directory, dirnames, filenames in os.walk(rootdir):
    dirnames[:] = sorted(dirnames)
    relpath_dir = os.path.relpath(directory, rootdir)
    if exclude_pattern and exclude_pattern.match(relpath_dir):
      continue

    for filename in filenames:
      if is_known_reject(filename):
        continue

      relpath_file = os.path.join(relpath_dir, filename)
      if relpath_dir == ".":
        relpath_file = filename

      if exclude_pattern and exclude_pattern.match(relpath_file):
        excluded.append(relpath_file)
        continue
      if has_known_extension(filename) or is_sentinel_name(filename):
        manifest.append(relpath_file)
        continue
  return manifest, excluded


def get_generated_manifest(rootdir):
  manifest = []
  for directory, dirnames, filenames in os.walk(rootdir):
    dirnames[:] = sorted(dirnames)
    relpath_dir = os.path.relpath(directory, rootdir)
    for filename in filenames:
      relpath_file = os.path.join(relpath_dir, filename)
      if filename.endswith(".lint-manifest"):
        fullpath_file = os.path.join(rootdir, relpath_file)
        with io.open(fullpath_file, "r", encoding="utf-8") as infile:
          manifest.extend(line.strip() for line in infile)
  return manifest


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("source_tree", help="path to the source directory")
  parser.add_argument("binary_tree", help="path to the binary directory")
  parser.add_argument("--exclude", nargs="*", help="exclusions")
  args = parser.parse_args()

  exclude_pattern = None
  if args.exclude:
    exclude_pattern = "|".join(args.exclude)
    exclude_pattern = re.compile(exclude_pattern)

  source_manifest, source_excluded = get_source_manifest(
      args.source_tree, exclude_pattern)
  gen_manifest = get_generated_manifest(args.binary_tree)

  source_set = set(source_manifest)
  gen_set = set(gen_manifest)

  missing = source_set.difference(gen_set)
  extra = gen_set.difference(source_set.union(source_excluded))

  returncode = 0
  if missing:
    logging.error(
        "The following files are missing from the generated manifests:"
        "\n  %s", "\n  ".join(sorted(missing)))
    returncode = 1
  if extra:
    logging.error(
        "The following files listed in the lint manifest are not found in"
        " the source tree:\n  %s", "\n  ".join(sorted(extra)))
    returncode = 1
  return returncode


if __name__ == "__main__":
  sys.exit(main())
