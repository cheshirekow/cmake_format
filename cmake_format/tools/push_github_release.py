"""
Create or modify the release for the currently built tag on travis.
"""

import argparse
import io
import logging
import os

import github
import magic

logger = logging.getLogger(__name__)

PSEUDO_MESSAGE = """
This is a pseudo-release used only to stage artifacts for the release pipeline.
Please do not rely on the artifacts contained in this release as they change
frequently and are very likely to be broken.
""".replace("\n", "")


def push_release(tag, message, filepaths):
  # TODO(josh): get slug out of the script so that it can be reusable
  reposlug = "cheshirekow/cmake_format"

  access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
  if access_token is None:
    raise RuntimeError("GITHUB_ACCESS_TOKEN missing from environment")

  # TODO(josh): get title out of the script so that it can be reusable
  if tag.startswith("pseudo-"):
    prerelease = True
    title = "pseudo-release artifacts for " + tag[len("pseudo-"):]
  else:
    prerelease = False
    title = "cmake-format " + tag

  filenames = set(filepath.rsplit(os.sep, 1)[-1] for filepath in filepaths)
  hub = github.Github(access_token)
  repo = hub.get_repo(reposlug)
  try:
    release = repo.get_release(tag)
    logger.info("Found release for tag %s", tag)
    if release.title != title or release.body != message:
      logger.info("Updating release message")
      release.update_release(title, message, prerelease=prerelease)
  except github.UnknownObjectException:
    logger.info("Creating release for tag %s", tag)
    release = repo.create_git_release(
        tag, title, message, prerelease=prerelease)

  for asset in release.get_assets():
    if asset.name in filenames:
      logger.info("Deleting asset %s", asset.name)
      asset.delete_asset()

  for filepath in filepaths:
    filename = filepath.rsplit(os.sep, 1)[-1]
    mime = magic.Magic(mime=True)
    release.upload_asset(
        filepath, content_type=mime.from_file(filepath), name=filename)


def main():
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument(
      "-m", "--message",
      help="path to a file containing release notes message")
  argparser.add_argument("tag", help="the tag we are deploying")
  argparser.add_argument("files", nargs="*", help="files to upload")
  args = argparser.parse_args()

  if args.message:
    with io.open(args.message, encoding="utf-8") as infile:
      message = infile.read()
  else:
    message = ""
  push_release(args.tag, message, args.files)


if __name__ == "__main__":
  main()
