# PYTHON_ARGCOMPLETE_OK
"""
Perform variable substitution in vscode configuration files
"""

import argparse
import io
import logging
import os
import re
import sys

logger = logging.getLogger(__name__)


def split_vars(varlist):
  out = {}
  for var in varlist:
    if "=" not in var:
      raise ValueError(
          "Invalid variable {}, should be in the form of <name>=<value>"
          .format(var))
    key, value = var.split("=")
    out[key] = value
  return out


def reverse_map(subtitutions):
  return {value: key for key, value in subtitutions.items()}


def subfile(content, substitutions):
  def subcallback(match):
    varname = match.group(1)
    return substitutions.get(varname, match.group(0))

  return re.sub(r"\$\{([^\}]+)\}", subcallback, content)


def unsubfile(content, substitutions):
  for varname, value in substitutions.items():
    content = content.replace(value, "${" + varname + "}")
  return content


def main():
  logging.basicConfig()

  argparser = argparse.ArgumentParser(description=__doc__)
  argparser.add_argument(
      "direction", choices=["sub", "unsub"], default="sub",
      help="whether to substitute values for variables or vice versa")
  argparser.add_argument(
      "--log-level", choices=["debug", "info", "warning", "error"],
      default="info")
  argparser.add_argument(
      "--var", action="append", dest="vars",
      help="variable to substitue in the form of <name>=<value>."
           " Can be repeated")
  argparser.add_argument(
      "--touch", action="append", default=[],
      help="a list of files to touch in addition")
  argparser.add_argument(
      "files", nargs="*", help="filepaths to modify")

  try:
    import argcomplete
    argcomplete.autocomplete(argparser)
  except ImportError:
    pass

  args = argparser.parse_args()
  logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

  if args.direction == "sub":
    subfn = subfile
  elif args.direction == "unsub":
    subfn = unsubfile
  else:
    raise ValueError("Unexpected direction {}".format(args.direction))

  substitutions = split_vars(args.vars)
  for filepath in args.files:
    with io.open(filepath, "r", encoding="utf-8") as infile:
      original_content = infile.read()
    new_content = subfn(original_content, substitutions)
    if new_content == original_content:
      logger.info("%s is unchanged", filepath)
      continue
    logger.info("rewriting %s", filepath)
    with io.open(filepath, "w", encoding="utf-8") as outfile:
      outfile.write(new_content)

  for filepath in args.touch:
    os.utime(filepath, None)

  return 0


if __name__ == "__main__":
  sys.exit(main())
