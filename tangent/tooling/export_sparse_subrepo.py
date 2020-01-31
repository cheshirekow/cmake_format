"""
Synchronize or validate a sparse subrepository export. The sparse export
configuration is stored in the `.sparse-export` file in the root of the
repository. If the file does not exist, then there is nothing to update
or verify.
"""

import argparse
import hashlib
import io
import logging
import os
import shutil
import subprocess
import sys

logger = logging.getLogger(__name__)


def setup_argparser(argparser):
  argparser.add_argument(
      "command", choices=["update", "verify"],
      help="whether to update or verify the export")


def get_argdict(args):
  out = {}
  for key, value in vars(args).items():
    if key.startswith("_"):
      continue
    out[key] = value
  return out


def copy_file(sourcepath, destpath):
  destdir = os.path.dirname(destpath)
  if not os.path.exists(destdir):
    os.makedirs(destdir)
  shutil.copy2(sourcepath, destpath)
  return 0


def read_chunks(infile, chunksize=4096):
  while True:
    chunk = infile.read(chunksize)
    if chunk == b'':
      break
    yield chunk


def hash_file(filepath, hashname="sha1", chunksize=4096):
  hashobj = hashlib.new(hashname)
  with open(filepath, "rb") as infile:
    for chunk in read_chunks(infile):
      hashobj.update(chunk)
  return hashobj


def verify_file(sourcepath, destpath):
  if not os.path.exists(destpath):
    logger.error("Missing %s", destpath)

  if hash_file(sourcepath).digest() == hash_file(destpath).digest():
    return 0
  logger.error("File %s differs from source", destpath)
  return 1


def inner_main(command):
  if command == "update":
    operation = copy_file
  elif command == "verify":
    operation = verify_file
  else:
    raise ValueError("Unknown command {}".format(command))

  repodir = subprocess.check_output(
      ["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")
  configfile = os.path.join(repodir, ".sparse-export")
  if not os.path.exists(configfile):
    return 0

  with io.open(configfile, "r", encoding="utf-8") as infile:
    relpath_export = infile.read().strip()
  export_dir = os.path.join(repodir, relpath_export)

  returncode = 0
  for directory, _dirnames, filenames in os.walk(export_dir):
    reldir = os.path.relpath(directory, export_dir)
    for filename in filenames:
      if reldir == ".":
        relpath_file = filename
      else:
        relpath_file = os.path.join(reldir, filename)

      sourcepath = os.path.join(directory, filename)
      if relpath_file == "sparse-checkout":
        relpath_file = ".gitu/info/sparse-checkout"
      destpath = os.path.join(repodir, relpath_file)
      returncode |= operation(sourcepath, destpath)
  return returncode


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
  return inner_main(**get_argdict(args))


if __name__ == "__main__":
  sys.exit(main())
