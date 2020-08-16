"""
Write out a pypirc file for use on travis. This allows us to use a different
password for each upload artifact, and between test.pypi.org and pypi.org
"""

import argparse
import io
import json

TEMPLATE = """\
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
username=__token__
password={}

[testpypi]
repository=https://test.pypi.org/legacy/
username=__token__
password={}
"""


def main():
  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument("--tokens-from")
  argparser.add_argument("--package")
  argparser.add_argument("-o", "--outfile")
  args = argparser.parse_args()

  with io.open(args.tokens_from, encoding="utf-8") as infile:
    data = json.load(infile)

  content = TEMPLATE.format(
      data["pypi.org"][args.package],
      data["test.pypi.org"][args.package])

  with io.open(args.outfile, "w", encoding="utf-8") as outfile:
    outfile.write(content)


if __name__ == "__main__":
  main()
