"""
Update dynamic parts of README.rst

Execute from the `cmake_format` project directory with something like:

python -B doc/update_readme.py
"""

import os
import re
import subprocess
import sys

def format_directive(content, codetag):
  outlines = [".. code:: {}".format(codetag), ""]
  for line in content.split("\n"):
    outlines.append(("    " + line).rstrip())
  outlines.append("")
  return "\n".join(outlines)

def main():
  docdir = os.path.dirname(os.path.realpath(__file__))
  projectdir = os.path.dirname(docdir)
  os.chdir(projectdir)
  env = os.environ.copy()
  env["PYTHONPATH"] = os.path.dirname(projectdir)

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

  with open("test/test_in.cmake") as infile:
    dynamic_text["example-in"] = format_directive(infile.read(), "cmake")
  with open("test/test_out.cmake") as infile:
    dynamic_text["example-out"] = format_directive(infile.read(), "cmake")

  tag_pattern = re.compile("^.. tag: (.*)-(begin|end)$")
  active_section = None
  with open("doc/README.rst", "r") as infile:
    with open("doc/README.rst.next", "w") as outfile:
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

  os.rename("doc/README.rst.next", "doc/README.rst")

if __name__ == "__main__":
  main()
