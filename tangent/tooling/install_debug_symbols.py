"""
Helper script called by cmake at install time to install debug binary
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--bin-path", help="path to the debug binary")
  parser.add_argument("--lib-dir", help="path to the install libdir")
  args = parser.parse_args()

  readelf_output = subprocess.check_output([
      "readelf", "-n", args.bin_path
  ]).decode("utf-8")

  lastline = readelf_output.strip().rsplit("\n", 1)[1]

  if not lastline.lstrip().startswith("Build ID:"):
    logging.error("readelf output doesn't end with BUILD ID")
    return 1
  buildid = lastline.split(":", 1)[1].strip()
  destdir = os.path.join(args.lib_dir, "debug/.build-id", buildid[:2])

  if "DESTDIR" in os.environ:
    destdir = os.path.join(os.environ["DESTDIR"], destdir.lstrip("/"))

  if not os.path.exists(destdir):
    os.makedirs(destdir)

  destpath = os.path.join(destdir, buildid[2:] + ".debug")
  if (os.path.exists(destpath) and
      os.path.getmtime(destpath) >= os.path.getmtime(args.bin_path)):
    print("-- Up-to-date: {}".format(destpath))
  else:
    print("-- Installing: {}".format(destpath))
    subprocess.check_call([
        "objcopy", "--only-keep-debug", args.bin_path, destpath])
  return 0


if __name__ == "__main__":
  logging.basicConfig(level=logging.WARNING)
  sys.exit(main())
