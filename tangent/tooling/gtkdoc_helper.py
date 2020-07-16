#!/usr/bin/env python

import argparse
import collections
import io
import logging
import os
import string
import sys

if __name__ == "__main__":
  # pylint: disable=import-error
  sys.path.append('/usr/share/gtk-doc/python')
  from gtkdoc import scangobj

logger = logging.getLogger(__name__)

TypesInfo = collections.namedtuple(
    "TypesInfo", ["includes", "forward_decls", "get_types"])


def parse_types(typespath):
  includes = []
  forward_decls = []
  get_types = []

  with io.open(typespath, "r", encoding="utf-8") as infile:
    for line in infile:
      line = line.strip()

      # comment or empty line
      if line.startswith("%") or not line.strip():
        continue

      # include line
      if line.startswith("#include"):
        includes.append(line)
        continue

      forward_decls.append('extern GType {}(void);'.format(line))
      get_types.append('  object_types[i++] = {}();'.format(line))

  return TypesInfo(includes, forward_decls, get_types)


def scangobj_run(args, outfile):
  typesinfo = parse_types(args.types)

  outfile.write(scangobj.COMMON_INCLUDES)
  outfile.write("\n".join(typesinfo.includes))
  outfile.write("\n".join(typesinfo.forward_decls))

  if args.query_child_properties:
    outfile.write(
        scangobj.QUERY_CHILD_PROPS_PROTOTYPE & args.query_child_properties)

  # substitute local vars in the template
  type_init_func = args.type_init_func
  main_func_params = "int argc, char *argv[]"
  if "argc" in type_init_func and "argv" not in type_init_func:
    main_func_params = "int argc, G_GNUC_UNUSED char *argv[]"
  elif "argc" not in type_init_func and "argv" in type_init_func:
    main_func_params = "G_GNUC_UNUSED int argc, char *argv[]"
  elif "argc" not in type_init_func and "argv" not in type_init_func:
    main_func_params = "void"

  tplargs = {
      "get_types": "\n".join(typesinfo.get_types),
      "ntypes": len(typesinfo.get_types),
      "main_func_params": main_func_params,
      "type_init_func": type_init_func,
  }

  for name in ("signals", "hierarchy", "interfaces", "prerequisites", "args"):
    tplargs["new_{}_filename".format(name)] = "{}.{}".format(args.module, name)

  main_content = string.Template(scangobj.MAIN_CODE).substitute(tplargs)
  outfile.write(main_content)

  if args.query_child_properties:
    outfile.write(
        scangobj.QUERY_CHILD_PROPS_CODE & args.query_child_properties)

  outfile.write(scangobj.MAIN_CODE_END)


def scangobj_main(args):
  """
  Replicate scangobj.run() with some simplifications and only up through the
  generation of the source code for <module>-scan.c. Don't compile and run
  the program.
  """
  outfile_path = os.path.join(
      args.output_dir, "{}-scan.c".format(args.module))

  with open(outfile_path, "w") as outfile:
    scangobj_run(args, outfile)


def setup_parser(argparser):
  subparsers = argparser.add_subparsers(dest="command")

  parser = subparsers.add_parser("scangobj")
  parser.add_argument(
      '--module', required=True,
      help='Name of the doc module being parsed')
  parser.add_argument(
      '--types', default='',
      help='The name of the file to store the types in')
  parser.add_argument(
      '--type-init-func', default='',
      help='The init function(s) to call instead of g_type_init()')
  parser.add_argument(
      '--query-child-properties', default='',
      help='A function that returns a list of child properties for a class')
  parser.add_argument(
      '--output-dir', default='.',
      help='The directory where the results are stored')


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  setup_parser(parser)
  args = parser.parse_args()

  if args.command == "scangobj":
    return scangobj_main(args)

  logger.warning("Unrecognized command %s", args.command)
  return 1


if __name__ == "__main__":
  sys.exit(main())
