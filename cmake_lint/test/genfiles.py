"""
Some of the test lint would get removed by my editor we have a little script to
help generate the file.
"""

import io
import os
import re


def make_expect_lint():
  thisdir = os.path.dirname(os.path.realpath(__file__))

  # strip test annotations from the test file make the documentation a little
  # cleaner
  with io.open(os.path.join(thisdir, "lint_tests.cmake"), newline='') as infile:
    content = infile.read()
  content = re.sub(
      "^# ((test)|(expect)): .*\n", "", content, flags=re.MULTILINE)
  with io.open(
      os.path.join(thisdir, "expect_lint.cmake"), "w", newline='') as outfile:
    outfile.write(content)


def rewrite_lint_tests():
  thisdir = os.path.dirname(os.path.realpath(__file__))

  # re-process the test file to re-introduce lint that is likely to have been
  # removed by an editor
  with io.open(os.path.join(thisdir, "lint_tests.cmake"), newline='') as infile:
    content = infile.read()

  lines = content.split("\n")
  have_changes = False

  # Need to remove newline
  if content[-1] == "\n":
    have_changes = True

  outlines = []
  for line in lines:
    if line.rstrip() == "# This line has the wrong line endings":
      if not line.endswith("\r"):
        line = line.rstrip() + "\r"
        have_changes = True

    if line.rstrip() == "# This line has trailing whitespace":
      if not line.endswith(" "):
        line = line.rstrip() + "   "
        have_changes = True
    outlines.append(line)

  if have_changes:
    while outlines and not outlines[-1].strip():
      outlines.pop(-1)
    with io.open(os.path.join(
        thisdir, "lint_tests.cmake"), "w", newline='') as outfile:
      outfile.write("\n".join(outlines))


def genfiles():
  rewrite_lint_tests()
  make_expect_lint()


if __name__ == "__main__":
  genfiles()
