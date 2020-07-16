"""
Modify a cmake-generated build system to insert our own every-run hook
into the generated build.
"""

import argparse
import io
import os
import resource
import sys
import time


def rewrite_ninja_build(binarydir):
  infilepath = os.path.join(binarydir, "build.ninja")
  outfilepath = infilepath + ".tmp"

  with io.open(outfilepath, "w", encoding="utf-8") as outfile:
    with io.open(infilepath, "r", encoding="utf-8") as infile:
      lineiter = iter(infile)
      for line in lineiter:
        outfile.write(line)
        if line.strip() == "# A missing CMake input file is not an error.":
          break

      # The next line should be a blank line
      outfile.write(next(lineiter, None))

      # Then this is the line we need to modify
      line = next(lineiter, None)
      line = line.replace("codestyle_manifest.cmake ", "")
      outfile.write(line)

      for line in lineiter:
        outfile.write(line)
  os.rename(outfilepath, infilepath)


MAKEFILE_RECIPE = (
    "\tcd $(CMAKE_SOURCE_DIR) && python -B"
    " {TANGENT_TOOLING}/generate_style_manifest.py"
    " --outfile $(CMAKE_BINARY_DIR)/codestyle_manifest.cmake"
    " --excludes-from $(CMAKE_SOURCE_DIR)/build_tooling/lint-excludes.txt"
    " -- $(CMAKE_SOURCE_DIR)\n")


def rewrite_makefiles(binarydir):
  infilepath = os.path.join(binarydir, "CMakeFiles/Makefile2")
  outfilepath = infilepath + ".tmp"

  with io.open(outfilepath, "w", encoding="utf-8") as outfile:
    with io.open(infilepath, "r", encoding="utf-8") as infile:
      lineiter = iter(infile)
      for line in lineiter:
        outfile.write(line)
        if line.strip() == "cmake_check_build_system:":
          break

      outfile.write(MAKEFILE_RECIPE.format(
          TANGENT_TOOLING=os.path.dirname(__file__)))

      for line in lineiter:
        outfile.write(line)
  os.rename(outfilepath, infilepath)


def daemon_main(args):
  if args.generator == "Ninja":
    rewrite_ninja_build(args.binary_dir)
  elif args.generator == "Unix Makefiles":
    rewrite_makefiles(args.binary_dir)


def main():
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("--test-mode", action="store_true")
  argparser.add_argument(
      "--binary-dir", required=True)
  argparser.add_argument(
      "--generator", required=True, choices=["Ninja", "Unix Makefiles"])
  args = argparser.parse_args()

  cmake_pid = os.getppid()
  process_id = os.fork()
  if process_id != 0:
    # this is the parent:
    sys.exit(0)

  # group_id = os.setpgrp()
  process_id = os.setsid()
  if process_id == -1:
    sys.exit(1)

  for fd in range(3, resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
    try:
      os.close(fd)
    except OSError:
      pass

  devnull_fd = os.open("/dev/null", os.O_RDWR)
  os.dup2(devnull_fd, 0)
  os.dup2(devnull_fd, 1)
  os.dup2(devnull_fd, 2)
  os.close(devnull_fd)
  # wait for cmake to die
  while os.path.exists("/proc/{}".format(cmake_pid)):
    if args.test_mode:
      break
    time.sleep(0.5)

  daemon_main(args)


if __name__ == "__main__":
  main()
