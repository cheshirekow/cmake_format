"""
Update dynamic parts of documentation files.
"""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import difflib
import io
import os
import re
import sys


def format_directive(content, codetag=None):
  # TODO(josh): change the indentation to 2 for some more compact files
  if codetag is None:
    codetag = ""
  if codetag == "table":
    outlines = [".. table:: ", "    :align: center", ""]
  else:
    outlines = [".. code:: {}".format(codetag), ""]
  for line in content.split("\n"):
    outlines.append(("    " + line).rstrip())
  outlines.append("")
  return "\n".join(outlines)


EXTENSION_TO_TAG = {
    ".txt": "text",
    ".py": "python",
    ".cmake": "cmake"
}


def get_dynamic_text(bitsdir, bittag):
  for filename in os.listdir(bitsdir):
    if not filename.startswith(bittag):
      continue

    inpath = os.path.join(bitsdir, filename)
    with io.open(inpath, "r", encoding="utf-8") as infile:
      content = infile.read()

    extension = filename[len(bittag):]
    if filename.endswith("-table.rst"):
      # TODO(josh): replace the following line with
      # codetag = "table"
      # so that tables are center aligned in the output
      return content
    if filename.endswith(".rst"):
      return content

    codetag = EXTENSION_TO_TAG.get(extension, None)
    return format_directive(content, codetag)
  raise RuntimeError("No dynamic text for bit {}".format(bittag))


def process_file(filepath, nextpath, bitsdir):
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
            content = get_dynamic_text(bitsdir, active_section)
            outfile.write(content)
            active_section = None
            outfile.write(line)
          else:
            raise RuntimeError("Unexpected tag")


def update_file(filepath, bitsdir):
  """
  Create a copy of the file replacing any dynamic sections with updated
  text. Then replace the original with the updated copy.
  """

  nextpath = filepath + ".next"
  process_file(filepath, nextpath, bitsdir)
  os.rename(nextpath, filepath)


def verify_file(filepath, bitsdir):
  """
  Create a copy of the file replacing any dynamic sections with updated
  text. Then verify that the copy is not different than the original
  """

  nextpath = filepath + ".tmp"
  process_file(filepath, nextpath, bitsdir)
  with io.open(filepath, "r", encoding="utf-8") as infile:
    lines_a = infile.read().split("\n")
  with io.open(nextpath, "r", encoding="utf-8") as infile:
    lines_b = infile.read().split("\n")
  os.unlink(nextpath)
  diff = list(difflib.unified_diff(lines_a, lines_b))
  if diff:
    raise RuntimeError("{} is out of date\n{}"
                       .format(filepath, "\n".join(diff)))


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--verify", action="store_true")
  parser.add_argument("--bits")
  parser.add_argument("filepath")
  args = parser.parse_args()

  if args.verify and sys.version_info < (3, 6, 0):
    print("Skipping verification on python < 3.6")
    sys.exit(0)

  if args.verify:
    verify_file(args.filepath, args.bits)
  else:
    update_file(args.filepath, args.bits)


if __name__ == "__main__":
  main()
