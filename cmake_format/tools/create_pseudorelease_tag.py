"""
Create a tag pseudo-<branch> pointing to the current head of <branch> on
github.
"""


import argparse
import logging
import os

import github

logger = logging.getLogger(__name__)

PSEUDO_MESSAGE = """
This is a pseudo-release used only to stage artifacts for the release pipeline.
Please do not rely on the artifacts contained in this release as they change
frequently and are very likely to be broken.
""".replace("\n", "")


def create_tag(branch):
  # TODO(josh): get slug out of the script so that it can be reusable
  reposlug = "cheshirekow/cmake_format"

  access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
  if access_token is None:
    raise RuntimeError("GITHUB_ACCESS_TOKEN missing from environment")

  # TODO(josh): get title out of the script so that it can be reusable
  hub = github.Github(access_token)
  repo = hub.get_repo(reposlug)
  branchobj = repo.get_branch(branch)
  logger.info("Creating tag pseudo-%s -> %s", branch, branchobj.commit.sha)
  refname = "tags/pseudo-" + branch
  try:
    existing_ref = repo.get_git_ref(refname)
    logger.info("Updating existing ref for %s", refname)
    existing_ref.edit(branchobj.commit.sha, force=True)
    return
  except github.UnknownObjectException:
    pass

  logger.info("Creating ref %s", refname)
  refname = "refs/" + refname
  repo.create_git_ref(refname, branchobj.commit.sha)


def main():
  logging.basicConfig(level=logging.INFO)
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("branch")
  args = argparser.parse_args()
  create_tag(args.branch)


if __name__ == "__main__":
  main()
