"""
Check ~/.pbuilderrc for some common advisable configurations
"""

import io
import os
import logging
import re

logger = logging.getLogger(__name__)


def get_extra_packages(content):
  extra_packages = []
  for line in content.split("\n"):
    line = line.strip()
    prefix = "EXTRAPACKAGES="
    if line.startswith(prefix):
      extra_packages.extend(line[len(prefix):].split(","))
  return extra_packages


def get_ldpreloads(content):
  preloads = []
  for line in content.split("\n"):
    line = line.strip()
    prefix = "export LD_PRELOAD="
    if line.startswith(prefix):
      value = line[len(prefix):].strip('"')
      value = re.sub(r"\$\{[^\}]*\}", "", value)
      preloads.extend(value.split(":"))
  return preloads


def main():
  filepath = os.path.expanduser("~/.pbuilderrc")
  if not os.path.exists(filepath):
    logger.warning(
        "No ~/.pbuilderrc in current build environment. It is highly"
        " recommended to include a ~/.pbuilderrc.")
    return

  with io.open(filepath, "r", encoding="utf-8") as infile:
    content = infile.read()

  extra_packages = get_extra_packages(content)
  if "eatmydata" not in extra_packages:
    logger.warning(".pbuilderrc missing EXTRAPACKAGES=eatmydata")

  ld_preloads = get_ldpreloads(content)
  if "libeatmydata.so" not in ld_preloads:
    logger.warning(
        '.pbuilderrc missing '
        '`export LD_PRELOAD="${LD_PRELOAD:+$LD_PRELOAD:}libeatmydata.so"`\n'
        'Contains: %s', ", ".join(ld_preloads))


if __name__ == "__main__":
  main()
