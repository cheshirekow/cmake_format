"""
Update dynamic parts of README.rst

Execute from the `cmake_format` project directory with something like:

python -B doc/update_readme.py
"""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import difflib
import io
import os
import re
import subprocess
import sys
import tempfile


def format_directive(content, codetag):
  outlines = [".. code:: {}".format(codetag), ""]
  for line in content.split("\n"):
    outlines.append(("    " + line).rstrip())
  outlines.append("")
  return "\n".join(outlines)


def process_file(filepath, nextpath, dynamic_text):
  """
  Write a copy of `filepath` to `nextpath` with substitutions from dynamic_text
  """
  tag_pattern = re.compile("^.. dynamic: (.*)-(begin|end)$")
  active_section = None

  with io.open(filepath, "r", encoding="utf-8") as infile:
    with io.open(nextpath, "w", encoding="utf-8") as outfile:
      for line in infile:
        match = tag_pattern.match(line.strip())
        if active_section is None:
          outfile.write(line)

        if match:
          if match.group(2) == "begin":
            active_section = match.group(1)
          elif match.group(2) == "end":
            assert active_section == match.group(1), "Unexpected end tag"
            outfile.write("\n")
            outfile.write(dynamic_text[active_section])
            active_section = None
            outfile.write(line)
          else:
            raise RuntimeError("Unexpected tag")


def update_file(filepath, dynamic_text):
  """
  Create a copy of the file replacing any dynamic sections with updated
  text. Then replace the original with the updated copy.
  """

  nextpath = filepath + ".next"
  process_file(filepath, nextpath, dynamic_text)
  os.rename(nextpath, filepath)


def verify_file(filepath, dynamic_text):
  """
  Create a copy of the file replacing any dynamic sections with updated
  text. Then verify that the copy is not different than the original
  """

  basename = os.path.basename(filepath)
  if "." in basename:
    prefix, suffix = basename.split(".", 1)
  else:
    prefix = basename
    suffix = None

  fd, nextpath = tempfile.mkstemp(prefix=prefix, suffix=suffix)
  os.close(fd)
  process_file(filepath, nextpath, dynamic_text)
  with io.open(filepath, "r", encoding="utf-8") as infile:
    lines_a = infile.read().split("\n")
  with io.open(nextpath, "r", encoding="utf-8") as infile:
    lines_b = infile.read().split("\n")

  diff = list(difflib.unified_diff(lines_a, lines_b))
  if diff:
    raise RuntimeError("{} is out of date".format(filepath))


DUMP_EXAMPLE = """
cmake_minimum_required(VERSION 3.5)
project(demo)
if(FOO AND (BAR OR BAZ))
  add_library(hello hello.cc)
endif()
"""


def generate_docsources(verify):
  """
  Process dynamic text sources and perform text substitutions
  """

  docdir = os.path.dirname(os.path.realpath(__file__))
  projectdir = os.path.dirname(docdir.rstrip(os.sep))
  repodir = os.path.dirname(projectdir.rstrip(os.sep))
  env = os.environ.copy()
  env["PYTHONPATH"] = repodir

  dynamic_text = {}
  dynamic_text["usage"] = format_directive(
      subprocess.check_output(
          [sys.executable, "-Bm", "cmake_format", "--help"], env=env
      ).decode("utf-8"),
      "text")
  dynamic_text["configuration"] = format_directive(
      subprocess.check_output(
          [sys.executable, "-Bm", "cmake_format", "--dump-config"], env=env
      ).decode("utf-8"),
      "text")

  with tempfile.NamedTemporaryFile(
      mode="w", delete=False) as outfile:
    outfile.write(DUMP_EXAMPLE)
    dump_example_src = outfile.name

  dynamic_text["dump-example-src"] = format_directive(DUMP_EXAMPLE, "cmake")
  for step in ("lex", "parse", "layout"):
    dynamic_text["dump-example-" + step] = format_directive(
        subprocess.check_output(
            [sys.executable, "-Bm", "cmake_format",
             "--dump", step, dump_example_src], env=env
        ).decode("utf-8"),
        "text"
    )

  with io.open(os.path.join(docdir, "features.rst"),
               encoding="utf-8") as infile:
    copylines = []
    for idx, line in enumerate(infile):
      if idx > 3:
        copylines.append(line)
    copylines.append("\n")
  dynamic_text["features"] = "".join(copylines)

  with io.open(
      os.path.join(projectdir, "test/test_in.cmake"),
      encoding="utf-8") as infile:
    dynamic_text["example-in"] = format_directive(infile.read(), "cmake")
  with io.open(
      os.path.join(projectdir, "test/test_out.cmake"),
      encoding="utf-8") as infile:
    dynamic_text["example-out"] = format_directive(infile.read(), "cmake")

  if verify:
    handle_file = verify_file
  else:
    handle_file = update_file

  for filename in (
      "doc/README.rst",
      "doc/usage.rst",
      "doc/example.rst",
      "doc/parse_tree.rst",
  ):
    handle_file(os.path.join(projectdir, filename), dynamic_text)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--verify", action="store_true")
  args = parser.parse_args()

  if args.verify and sys.version_info < (3, 5, 0):
    print("Skipping verification on python < 3.5")
    sys.exit(0)

  generate_docsources(args.verify)


if __name__ == "__main__":
  main()
