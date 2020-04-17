"""
Scan the source tree rooted at a particulary directory and build a list of all
lintable files. Compare that list against the list of names in any
`.lint-manifest` in the binary tree. If the two are not identical, exit with
nonzero status code.
"""

from __future__ import absolute_import, unicode_literals

import argparse
import difflib
import io
import os
import re
import shlex
import sys

SLUGS = ["BZL", "CMAKE", "CC", "JS", "PY", "SHELL"]


def invert_map(sourcemap):
  out = {}
  for slug, extensions in sourcemap.items():
    for extension in extensions:
      out[extension] = slug
  return out


KNOWN_EXTENSIONS = {
    "BZL": [".bzl"],
    "CMAKE": [".cmake"],
    "CC": [".c", ".cc", ".cxx", ".cpp", ".h", ".hxx", ".hpp", ".tcc"],
    "JS": [".js"],
    "PY": [".py"],
    "SHELL": [".sh"]
}

EXTENSION_MAP = invert_map(KNOWN_EXTENSIONS)


def get_slug_from_extension(filename):
  tail = filename
  if os.sep in tail:
    tail = tail.rsplit(os.sep, 1)[1]

  parts = tail.split(".")
  while parts:
    parts[0] = ""
    candidate_extension = ".".join(parts).lower()
    slug = EXTENSION_MAP.get(candidate_extension, None)
    if slug is not None:
      return slug
    parts.pop(0)

  return None


def get_slug_from_shebang(filepath):
  with io.open(filepath, "rb") as infile:
    shebang = infile.read(2)
    if shebang != b"#!":
      return None
    interp = infile.readline().strip().decode("utf-8")
  parts = shlex.split(interp)
  if len(parts) == 2:
    if parts[0] == "/usr/bin/env":
      if parts[1] == "python":
        return "PY"
      elif parts[1] == "bash":
        return "SHELL"
  else:
    if interp.startswith("/usr/bin/python"):
      return "PY"
    if interp in ["/bin/bash", "/bin/sh"]:
      return "SHELL"
  return None


KNOWN_NAMES = {
    "BZL": ["BUILD", "WORKSPACE"],
    "CMAKE": ["CMakeLists.txt"]
}

NAME_MAP = invert_map(KNOWN_NAMES)


def get_slug_from_name(filename):
  return NAME_MAP.get(filename, None)


REJECT_NAMES = [
    # Outputs of cmake in-source configure
    "CTestTestfile.cmake",
    "cmake_install.cmake",
]


def is_known_reject(filename):
  return filename in REJECT_NAMES


REJECT_DIRS = [
    "build",
    ".git",
    ".build",
    "__pycache__",
]


def get_source_manifest(rootdir, exclude_pattern):
  manifest = {slug: [] for slug in SLUGS}
  excluded = []

  for directory, dirnames, filenames in os.walk(rootdir):
    dirnames[:] = sorted(dirnames)
    relpath_dir = os.path.relpath(directory, rootdir)

    if os.sep in directory:
      dirname = directory.rsplit(os.sep, 1)[1]
    else:
      dirname = directory

    # NOTE(josh): on buildbot, the source directory is called "build"... ugh.
    if dirname in REJECT_DIRS and directory != rootdir:
      excluded.append(relpath_dir)
      dirnames[:] = []
      continue

    if exclude_pattern and exclude_pattern.match(relpath_dir):
      excluded.append(relpath_dir)
      dirnames[:] = []
      continue

    for filename in filenames:
      if is_known_reject(filename):
        continue

      relpath_file = os.path.join(relpath_dir, filename)
      fullpath_file = os.path.join(directory, filename)

      if os.path.islink(fullpath_file):
        continue

      if relpath_dir == ".":
        relpath_file = filename

      if exclude_pattern and exclude_pattern.match(relpath_file):
        excluded.append(relpath_file)
        continue

      slug = get_slug_from_extension(filename)
      if slug is None:
        slug = get_slug_from_name(filename)
      if slug is None:
        slug = get_slug_from_shebang(fullpath_file)

      if slug is not None:
        manifest[slug].append(relpath_file)

  return manifest, excluded


def write_manifest(outfile, manifest, excluded):
  outfile.write("format_and_lint(main\n")
  for slug, filenames in sorted(manifest.items()):
    if not filenames:
      continue
    outfile.write("  {}\n".format(slug))
    for filename in sorted(filenames):
      outfile.write("    {}\n".format(filename))
  outfile.write(")\n")

  if not excluded:
    return

  outfile.write("\n")
  outfile.write("NOTE: The following were excluded\n")
  for filename in sorted(excluded):
    outfile.write("# {}\n".format(filename))


DEFAULT_EXCLUDES = [
    r".*\.egginfo",
]


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "-o", "--outfile-path", default="-",
      help="file to write the generated manifest")
  parser.add_argument(
      "--show-exclusions", action="store_true",
      help="include a list of excluded files in the output")

  parser.add_argument("--excludes", nargs="*", help="exclusions")
  parser.add_argument("--excludes-from", help="exclusions file")
  parser.add_argument("source_tree", help="path to the source directory")
  args = parser.parse_args()

  excludes = list(DEFAULT_EXCLUDES)
  if args.excludes:
    excludes.extend(args.exclude)
  if args.excludes_from:
    with io.open(args.excludes_from, "r", encoding="utf-8") as infile:
      for line in infile:
        line = line.strip()
        if not line:
          continue
        if line.startswith("#"):
          continue
        excludes.append(line)

  exclude_pattern = "|".join(excludes)
  exclude_pattern = re.compile(exclude_pattern)

  manifest, excluded = get_source_manifest(args.source_tree, exclude_pattern)

  buffer = io.StringIO()
  if not args.show_exclusions:
    excluded = []
  write_manifest(buffer, manifest, excluded)
  outfile_content = buffer.getvalue()

  if args.outfile_path == "-":
    sys.stdout.write(outfile_content)
    return 0

  if os.path.isfile(args.outfile_path):
    with io.open(args.outfile_path, "r", encoding="utf-8") as infile:
      existing_content = infile.read()
    if existing_content == outfile_content:
      return 0

    for line in difflib.unified_diff(
        existing_content.split("\n"), outfile_content.split("\n")):
      line = line.rstrip("\n")
      print(line)

  with io.open(args.outfile_path, "w", encoding="utf-8") as outfile:
    outfile.write(outfile_content)


if __name__ == "__main__":
  sys.exit(main())
