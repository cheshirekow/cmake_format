"""
Given a staging directory and a file containing a list of what should be in
that directory, delete any files that shouldn't be there.
"""

import argparse
import io
import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_argparser(argparser):
  argparser.add_argument(
      "manifest_path", help="path to the manifest file")
  argparser.add_argument(
      "stage_path", help="path to the staging directory")


def get_argdict(args):
  out = {}
  for key, value in vars(args).items():
    if key.startswith("_"):
      continue
    out[key] = value
  return out


def inner_main(manifest_path, stage_path):
  with io.open(manifest_path, "r", encoding="utf-8") as infile:
    manifest = set(line.strip() for line in infile)

  for directory, _dirnames, filenames in os.walk(stage_path):
    relpath_dir = os.path.relpath(directory, stage_path)

    for filename in filenames:
      if relpath_dir == ".":
        relpath_file = filename
      else:
        relpath_file = os.path.join(relpath_dir, filename)
      fullpath_file = os.path.join(directory, filename)

      if relpath_file not in manifest and fullpath_file not in manifest:
        logger.info("Deleting %s", relpath_file)
        os.unlink(fullpath_file)


def main():
  logging.basicConfig(level=logging.INFO)
  argparser = argparse.ArgumentParser(description=__doc__)
  setup_argparser(argparser)
  try:
    import argcomplete
    argcomplete.autocomplete(argparser)
  except ImportError:
    pass
  args = argparser.parse_args()
  inner_main(**get_argdict(args))
  return 0


if __name__ == "__main__":
  sys.exit(main())
