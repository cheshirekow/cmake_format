# -*- coding: utf-8 -*-
"""
Helper scripts for building debian packages. Provides a number of frontend
commands that are called by the cmake generated build system to work through
the different stages of building the debian packages.
"""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import io
import logging
import math
import os
import re
import subprocess
import sys
import time

import enum
import requests

logger = logging.getLogger(__name__)


def parse_changelog(logpath):
  """
  Parse the changelog to get package name and version number
  """
  with io.open(logpath, "r", encoding="utf-8") as infile:
    lineiter = iter(infile)
    firstline = next(lineiter)

  pattern = r"(\S+) \(([^\)]+)\) (\S+); urgency=\S+"
  match = re.match(pattern, firstline)
  assert match, "Failed to match firstline pattern:\n {}".format(firstline)

  package_name = match.group(1)
  version = match.group(2)
  distribution = match.group(3)

  if "-" in version:
    upstream_version, debian_revision = version.rsplit("-", 1)
  else:
    upstream_version = version
    debian_revision = 0

  return package_name, upstream_version, debian_revision, distribution


class Flags(enum.IntEnum):
  EXCLUDE = 0b1
  DIRECTORY = 0b01


def should_include(patterns, relpath, query_flags=0):
  """
  Return true if a directory should be included
  """
  most_recent_positive_match = None

  output = False
  if query_flags & Flags.DIRECTORY:
    output = True

  for flags, regex in patterns:
    if (flags & Flags.DIRECTORY and
        not query_flags & Flags.DIRECTORY):
      continue

    if not regex.fullmatch(relpath):
      continue

    if flags & Flags.EXCLUDE:
      output = False
    else:
      most_recent_positive_match = regex
      output = True

  if output and not (query_flags & Flags.DIRECTORY):
    logger.debug("%s matched by %s", relpath, most_recent_positive_match)

  return output


def gentree(sourcedir, patterns):
  exclude = re.compile("|".join("({})".format(pat) for pat in [
      r"\.build",
      r"\.git",
      r"\.vscode",
      # python poop
      r"__pycache__",
      # autosaves
      r".*~$",
      r"\.ipynb_checkpoints",
      # bazel poop
      "bazel-.*",
      "WORKSPACE",
      # python packaging
      r".*\.egg-info",
      "build",
      "dist",
      # node poop
      "node_modules",
  ]))

  for dirpath, dirnames, filenames in os.walk(sourcedir):
    relpath_parent = os.path.relpath(dirpath, sourcedir)
    if relpath_parent == ".":
      relpath_parent = ""

    filtered_dirs = []
    for dirname in sorted(dirnames):
      if exclude.fullmatch(dirname):
        continue
      reldir = os.path.join(relpath_parent, dirname)
      if not should_include(patterns, reldir, Flags.DIRECTORY):
        continue
      filtered_dirs.append(dirname)
    dirnames[:] = filtered_dirs

    for filename in sorted(filenames):
      if exclude.fullmatch(filename):
        continue
      relpath = os.path.join(relpath_parent, filename)
      if not should_include(patterns, relpath):
        continue
      yield relpath


def get_patterns_from(globspath):
  """
  Read a file containing globbing patterns and return the patterns as a list
  of strings
  """
  patterns = []
  with io.open(globspath, "r", encoding="utf-8") as infile:
    for line in infile:
      line = line.strip()
      if not line:
        continue
      if line.startswith("#"):
        continue
      patterns.append(line)
  return patterns


def translate_patterns(lines):
  """
  Translate a list of (possibly negated) globbing patterns into a list of
  regular expressions
  """
  patterns = []
  for line in lines:
    flags = 0
    if line.startswith("!"):
      line = line.lstrip("!")
      flags |= Flags.EXCLUDE
    if line.endswith("/"):
      line = line.rstrip("/")
      flags |= Flags.DIRECTORY

    # Convert shell glob to regular expression. See
    # http://man7.org/linux/man-pages/man7/glob.7.html

    # "**" matches any number of characters
    filtered_parts = []
    for part in re.split(r"((?:\*\*)|/)", line):
      if part == "**":
        filtered_parts.append(".*")
      elif part == "/":
        filtered_parts.append("/")
      else:
        # If a right square bracket is the first character in a character
        # class it is literal (e.g. part of the character class)
        part = re.sub(r"(\[!)\]", r"\1\]", part)

        # [!...] is a negated character class
        part = part.replace("[!", "[^")

        # dots are literal
        part = part.replace(".", r"\.")

        # '*' matches zero or more of anything but path separator
        part = part.replace("*", "[^/]*")

        # '?' matches zero or one of anything but path separator
        part = part.replace("?", "[^/]?")

        filtered_parts.append(part)

    translated = "".join(filtered_parts)
    patterns.append((flags, re.compile(translated)))
  return patterns


def check_manifest(treegen, sourcedir, outpath):
  latest_mtime = 0
  tmppath = outpath + ".tmp"
  with io.open(tmppath, "w", encoding="utf-8") as outfile:
    for relpath in treegen:
      outfile.write(relpath)
      outfile.write("\n")
      fullpath = os.path.join(sourcedir, relpath)
      latest_mtime = max(latest_mtime, os.path.getmtime(fullpath))

  if subprocess.call(["cmp", "--silent", outpath, tmppath]) != 0:
    print("tarball manifest is out of date")
    os.rename(tmppath, outpath)
    return

  if os.path.getmtime(outpath) < latest_mtime:
    print("tarball content is out of date")
    os.rename(tmppath, outpath)
    return


def translate_changelog(src, dst, distro):
  parent = os.path.dirname(dst)
  if not os.path.exists(parent):
    os.makedirs(parent)

  pattern = r"(\S+) \(([^\)]+)\) ubuntu; (urgency=\S+)"
  replacement = r"\1 (\2~{0}) {0}; \3".format(distro)
  entry_regex = re.compile(pattern)
  with open(src, "r") as infile:
    with open(dst, "w") as outfile:
      for line in infile:
        outfile.write(entry_regex.sub(replacement, line))


def setup_argparse(parser):
  """
  Setup argument parser
  """
  parser.add_argument(
      "--log-level", default="info",
      choices=["debug", "info", "warning", "error"])
  parser.add_argument("-o", "--outpath", help="path to output file")
  subparsers = parser.add_subparsers(dest="command")
  subparser = subparsers.add_parser(
      "parse-changelog",
      help=("Parse a debian changelog to get the package name and version"
            " numbers. Output a cmake snippet that can be include()ed"))
  subparser.add_argument("logpath")
  subparser.add_argument("prefix")

  subparser = subparsers.add_parser(
      "check-manifest",
      help=("Scan the source tree for the list of files that go into the source"
            " package. If the file set has changed, or if any of the files have"
            " changed, then touch the manifest file"))
  mutex = subparser.add_mutually_exclusive_group()
  mutex.add_argument(
      "--patterns-from", help="File containing a  list of pattenrs")
  mutex.add_argument(
      "--patterns", nargs="*", help="Patterns on the command line")
  subparser.add_argument("sourcedir")

  subparser = subparsers.add_parser(
      "translate-changelog",
      help=("Copy debian changelog and replace the most recent header line "
            "with the desired distribution"))
  subparser.add_argument("--src", help="source file")
  subparser.add_argument("--tgt", help="target/destination path")
  subparser.add_argument("--distro", help="distribution")


PARSE_CHANGELOG_FORMAT = """
set({0}_package {1})
set({0}_version {2})
set({0}_debversion {3})
"""


def parse_changelog_cmdfn(args):
  info = parse_changelog(args.logpath)
  with io.open(args.outpath, "w", encoding="utf-8") as outfile:
    outfile.write(
        PARSE_CHANGELOG_FORMAT.format(args.prefix, *info[:3]))
  return 0


def check_manifest_cmdfn(args):
  if args.patterns_from:
    lines = get_patterns_from(args.patterns_from)
  else:
    lines = args.patterns
  patterns = translate_patterns(lines)
  for _, pattern in patterns:
    logger.debug("%s", pattern)
  treegen = gentree(args.sourcedir, patterns)
  check_manifest(treegen, args.sourcedir, args.outpath)
  return 0


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser(description=__doc__)
  setup_argparse(parser)
  args = parser.parse_args()
  logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

  if args.command == "parse-changelog":
    return parse_changelog_cmdfn(args)
  elif args.command == "check-manifest":
    return check_manifest_cmdfn(args)
  elif args.command == "translate-changelog":
    translate_changelog(args.src, args.tgt, args.distro)
  else:
    logging.error("Unknown command: {}".format(args.command))
    return 1

  return 0


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
  sys.exit(main())


#
#
#
#
#
#
#
#
#
#
#
#
#
#


def get_progress_bar(fraction, numchars=30):
  """
  Return a high resolution unicode progress bar
  """
  blocks = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
  length_in_chars = fraction * numchars
  if length_in_chars > numchars:
    length_in_chars = numchars
  n_full = int(length_in_chars)

  i_partial = int(len(blocks) * (length_in_chars - n_full))
  partial = blocks[i_partial]
  n_empty = max(numchars - n_full - len(partial), 0)
  return ("█" * n_full) + partial + (" " * n_empty)


def get_human_readable_size(size_in_bytes):
  """
  Convert a number of bytes into a human readable string.
  """
  if size_in_bytes == 0:
    return '{:6.2f}{}'.format(0, " B")

  exponent = int(math.log(size_in_bytes, 1024))
  unit = [' B', 'KB', 'MB', 'GB', 'PB', 'EB'][exponent]
  size_in_units = float(size_in_bytes) / (1024 ** exponent)
  return '{:6.2f}{}'.format(size_in_units, unit)


def download_file(srcurl, outpath):
  """
  Download <package>-<version>.tar.gz if it doesn't already exist
  """
  tmppath = outpath + ".tmp"
  if os.path.exists(tmppath):
    os.remove(tmppath)

  response = requests.head(srcurl)
  totalsize = int(response.headers.get("content-length", 2320000))
  recvsize = 0

  request = requests.get(srcurl, stream=True)
  last_print = 0

  outname = os.path.basename(outpath)
  with open(tmppath, "wb") as outfile:
    for chunk in request.iter_content(chunk_size=4096):
      outfile.write(chunk)
      recvsize += len(chunk)

      if time.time() - last_print > 0.1:
        last_print = time.time()
        percent = 100.0 * recvsize / totalsize
        message = ("Downloading {}: {}/{} [{}] {:6.2f}%"
                   .format(outname,
                           get_human_readable_size(recvsize),
                           get_human_readable_size(totalsize),
                           get_progress_bar(percent / 100.0), percent))
        sys.stdout.write(message)
        sys.stdout.flush()
        sys.stdout.write("\r")
  message = ("Downloading {}: {}/{} [{}] {:6.2f}%"
             .format(outname,
                     get_human_readable_size(totalsize),
                     get_human_readable_size(totalsize),
                     get_progress_bar(1.0), 100.0))
  sys.stdout.write(message)
  sys.stdout.write("\n")
  sys.stdout.flush()
  os.rename(tmppath, outpath)
  return outpath


def get_base_tgz(distro, arch):
  return "/var/cache/pbuilder/{}-{}-base.tgz".format(distro, arch)


def prep_pbuilder(distro, arch, basetgz):
  """
  Create base rootfs tarfiles for the specified distro/arch.
  """
  subprocess.check_call(
      ["sudo", "pbuilder", "--create", "--distribution", distro,
       "--architecture", arch, "--basetgz", basetgz])


def exec_pbuilder(dscpath, distro, arch, basetgz, outdir):
  """
  Execute pbuilder to get the binary archives
  """
  subprocess.check_call(
      ["sudo", "env", 'DEB_BUILD_OPTIONS="parallel=8"',
       "pbuilder", "--build", "--distribution", distro,
       "--architecture", arch, "--basetgz", basetgz,
       "--buildresult", outdir, dscpath])


def build_arch(distro, arch, args, dscpath, package_name, upstream_version,
               local_version):
  workdir = os.path.join(args.out, distro)

  # Create the base tarball if needed
  basetgz = get_base_tgz(distro, arch)
  outname = os.path.basename(basetgz)
  if os.path.exists(basetgz):
    logger.info("%s up to date", outname)
  else:
    logger.info("Making %s", outname)
    prep_pbuilder(distro, arch, basetgz)

  outname = ("{}_{}-{}_{}.deb"
             .format(package_name, upstream_version, local_version, arch))

  binout = os.path.join(workdir, 'binary')
  if not os.path.exists(binout):
    os.makedirs(binout)

  outpath = os.path.join(binout, outname)
  needs_build = False
  if os.path.exists(outpath):
    if os.stat(outpath).st_mtime < os.stat(dscpath).st_mtime:
      needs_build = True
      logger.info("%s is out of date", outname)
    else:
      logger.info("%s is up to date", outname)
  else:
    needs_build = True
    logger.info("Need to create %s", outname)

  if needs_build:
    exec_pbuilder(dscpath, distro, arch, basetgz, binout)

  logger.info("Writing out repository index")
  with open(os.path.join(binout, "Packages.gz"), "wb") as outfile:
    scanpkg = subprocess.Popen(
        ["dpkg-scanpackages", "."], cwd=binout, stdout=subprocess.PIPE)
    gzip = subprocess.Popen(
        ["gzip", "-9c"], cwd=binout, stdout=outfile, stdin=scanpkg.stdout)
    scanpkg.stdout.close()
  scanpkg.wait()
  gzip.wait()


def build_for(distro, args, tarball):
  logger.info("Building for %s", distro)
  workdir = os.path.join(args.out, distro)
  if not os.path.exists(workdir):
    os.makedirs(workdir)

  # Extract the tarball
  srcdir = os.path.join(workdir, "i3-{}".format(UPSTREAM_VERSION))
  if os.path.exists(srcdir):
    logger.info("Already extracted tarball")
  else:
    logger.info("Extracting tarball")
    subprocess.check_call(["tar", "xf", tarball], cwd=workdir)

  # Create symlink to source
  tarname = os.path.basename(tarball)
  tarlink = os.path.join(workdir, tarname)
  if not os.path.lexists(tarlink):
    os.symlink(tarball, tarlink)

  # Synchronize patches
  logger.info("Syncing debian patches")
  subprocess.check_call([
      'rsync', "-a",
      os.path.join(args.src, "debian/"),
      os.path.join(srcdir, "debian/")
  ])

  # Translate the changelog into ubuntu suite names
  src_changelog = os.path.join(args.src, "debian/changelog")
  srcdir = os.path.join(workdir, "i3-{}".format(UPSTREAM_VERSION))
  dst_changelog = os.path.join(srcdir, "debian/changelog")
  translate_changelog(src_changelog, dst_changelog, distro)

  # Create the .dsc file
  (package_name, upstream_version, local_version,
      distribution) = parse_changelog(dst_changelog)
  if distro != distribution:
    raise RuntimeError("{} != {}".format(distro, distribution))

  outname = ("{}_{}-{}.dsc"
             .format(package_name, upstream_version, local_version))
  dscpath = os.path.join(workdir, outname)
  if os.path.exists(dscpath):
    logger.info("%s already built", outname)
  else:
    logger.info("Creating %s", outname)
    subprocess.check_call(['debuild', "-S", "-sa", "-pgpg2", "-k6A8A4FAF"],
                          cwd=srcdir)

  if args.skip_build:
    return
  for arch in args.arch:
    build_arch(distro, arch, args, dscpath, package_name, upstream_version,
               local_version)


def download_if_needed(src_url, out):
   # Download the tarball if needed
  if src_url:
    filename = src_url.rsplit("/", 1)[1]
    basename = filename[:-len(".tar.gz")]
    tarball = os.path.join(out, basename + ".orig.tar.gz")
    if not os.path.exists(out):
      os.makedirs(out)
    if os.path.exists(tarball):
      logger.info("Already downloaded tarball")
    else:
      download_file(src_url, tarball)
