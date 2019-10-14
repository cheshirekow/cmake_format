"""
Find all restructured text files and write them out to a manifest
"""

import argparse
import os

EXCLUDE_DIRS = [
    ".build",
    ".git"
]

def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("-m", "--manifest-path",
                      help="Path to the manifest file to create/update")
  parser.add_argument("-t", "--touch", action="store_true",
                      help="Touch the manifest if any rst files are newer")
  parser.add_argument("rootdir")
  args = parser.parse_args()

  rootdir = os.path.realpath(args.rootdir)

  latest_mtime = 0

  fileset = set()
  for parent, dirnames, filenames in os.walk(rootdir):
    dirnames[:] = sorted(dirnames)
    relpath_parent = os.path.relpath(parent, rootdir)
    if relpath_parent in EXCLUDE_DIRS:
      dirnames[:] = []
      continue

    for filename in filenames:
      if filename.endswith(".rst"):
        if relpath_parent == ".":
          relpath_file = filename
        else:
          relpath_file = os.path.join(relpath_parent, filename)
        file_mtime = os.path.getmtime(os.path.join(rootdir, relpath_file))
        latest_mtime = max(latest_mtime, file_mtime)
        fileset.add(relpath_file)

  manifest_mtime = 0
  manifest_path = os.path.realpath(args.manifest_path)
  manifest_set = set()
  if os.path.exists(manifest_path):
    manifest_mtime = os.path.getmtime(manifest_path)
    with open(manifest_path, "r") as infile:
      for line in infile:
        manifest_set.add(line.strip())

  if manifest_set != fileset:
    print("RST manifest has changed")
    with open(manifest_path, "w") as outfile:
      for relpath_file in sorted(fileset):
        outfile.write(relpath_file)
        outfile.write("\n")
  elif args.touch and latest_mtime > manifest_mtime:
    print("An RST file has changed")
    os.utime(manifest_path, None)

if __name__ == "__main__":
  main()
