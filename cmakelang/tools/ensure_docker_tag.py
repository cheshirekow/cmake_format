"""
Ensure that the precommit repository is up-to-date with the released versions
of cmakelang.
"""

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

from packaging import version as versiontool

logger = logging.getLogger(__name__)


def get_env(deploykey_path):
  env = os.environ.copy()
  if deploykey_path:
    env["GIT_SSH_COMMAND"] = (
        "ssh -o IdentitiesOnly=yes -i {} -F /dev/null".format(deploykey_path))
  return env


def get_upstream_versions(remote, deploykey_path):
  versions = []
  regex = re.compile(r"^\w{40}\s*refs/tags/v(.*)$")

  tag_pairs = subprocess.check_output(
      ["git", "ls-remote", "--tags", remote], env=get_env(deploykey_path)
  ).decode("utf-8").split("\n")

  for line in tag_pairs:
    match = regex.match(line.strip())
    if not match:
      continue

    try:
      version = versiontool.parse(match.group(1))
    except versiontool.InvalidVersion:
      continue

    versions.append(version)
  return sorted(versions)


def inner_main(workdir, versionstr, deploykey_path, dry_run, keep):
  version = versiontool.parse(versionstr)
  remote = "git@github.com:cheshirekow/cmake-format-docker"

  upstream_versions = get_upstream_versions(remote, deploykey_path)
  if not upstream_versions:
    logging.error("Received empty list of upstream versions")
    return 1

  if version in upstream_versions:
    logger.info(
        "Desired version tag %s already exists on the origin,"
        " nothing to do", version)
    return 0

  latest_upstream_version = upstream_versions[-1]
  if version < latest_upstream_version:
    logger.warning(
        "Desired version tag %s is behind the latest deployed version %s",
        version, latest_upstream_version)

  if os.path.exists(workdir):
    shutil.rmtree(workdir)

  os.makedirs(workdir)
  subprocess.check_call(["git", "init"], cwd=workdir)
  subprocess.check_call(["git", "remote", "add", "origin", remote], cwd=workdir)
  subprocess.check_call(
      ["git", "fetch", "--depth=1", "origin", "master"], cwd=workdir)
  subprocess.check_call(
      ["git", "checkout", "master"], cwd=workdir)

  subprocess.check_call(
      ["git", "tag", "v" + versionstr], cwd=workdir)

  if dry_run:
    logging.info("Skiping push of tag %s", "v" + versionstr)
  else:
    subprocess.check_call(
        ["git", "push", "origin", "v" + versionstr], cwd=workdir,
        env=get_env(deploykey_path))

  if keep:
    logging.info("Leaving work tree at %s", workdir)
  else:
    shutil.rmtree(workdir)
  return 0


def main():
  logging.basicConfig(level=logging.INFO)

  default_workdir = os.path.join(tempfile.gettempdir(), "scratch-work")
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("--version", help="Which version")
  argparser.add_argument(
      "--workdir", default=default_workdir,
      help="Directory we can use for work")
  argparser.add_argument(
      "--dry-run", action="store_true", help="Don't push when done")
  argparser.add_argument(
      "--keep", action="store_true", help="keep the worktree around")
  argparser.add_argument(
      "--deploykey", help="path to the deploykey", nargs="?")
  args = argparser.parse_args()

  version = args.version
  if version == "from-travis-tag":
    version = os.environ["TRAVIS_TAG"]
  return inner_main(
      args.workdir, version, args.deploykey, args.dry_run, args.keep)


if __name__ == "__main__":
  sys.exit(main())
