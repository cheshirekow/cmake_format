"""General utilities for bazel"""

def tangent_fetchobj(uuid, filename):
  """Download an artifact from openstack objecstore"""

  command = " ".join([
    "swift",
    "--os-auth-url=https://auth.cloud.ovh.net/v3/",
    "--os-identity-api-version=3",
    "--os-region-name=BHS",
    "--os-tenant-id=b5e0ef36abcb498b890d84b61555f063",
    "--os-tenant-name=0728979165260176",
    "--os-username=user-px7eRuuMs4hy",
    "--os-password=HHScMqa9DHaAphNqQx6YpaRsMVE4AakH",
    "download tangent-build",
    uuid,
    "-o $(RULEDIR)/{}".format(filename),
  ])
  native.genrule(
    name = "fetch-" + filename,
    outs = [filename],
    cmd = command,
    visibility = ["//visibility:public"],
  )

def tangent_extract_svg(
    output = None,
    src = None,
    export = None):
  """Use inkscape to extract a subset of an SVG into it's own SVG file.

     This is
     useful for working on multiple icons in a single SVG and then splitting
     them into separate SVGs at build time

  Args:
    output: path to the output .svg to create
    src: path to the input .svg containing the desired object
    export: id of the SVG element to export
  """

  native.genrule(
    name = "inkscape-extract-" + output,
    outs = [output],
    cmd = " ".join([
      "inkscape",
      "--export-plain-svg=$@",
      "--export-id=" + export,
      "--export-id-only",
      "$<",
    ]),
    srcs = [src],
    visibility = ["//visibility:public"],
  )

def tangent_gresource(
    basename = None,
    xmlfile = None,
    srcdirs = None,
    deps = None):
  """Use glib-compile-resources to create a resource pack

  Args:
    basename: the basename used for the .h and .c files
    xmlfile: the .gresource.xml file specification of the resource pack
    srcdirs: the source directories to which the resource files are relative
            when specified in xmlfile
    deps: a list of files that will go into the resource pack, on which this
          rule depends
  """

  cmdparts = ["glib-compile-resources", "--generate"]
  for srcdir in srcdirs:
    cmdparts.append("--sourcedir=" + srcdir)
  cmdparts.append("$(location " + xmlfile + ")")
  cmdparts.append("--target=$@")

  native.genrule(
    name = "gresource-" + basename + ".h",
    outs = [basename + ".h"],
    cmd = " ".join(cmdparts),
    srcs = [xmlfile] + deps,
    visibility = ["//visibility:public"],
  )

  native.genrule(
    name = "gresource-" + basename + ".c",
    outs = [basename + ".c"],
    cmd = " ".join(cmdparts),
    srcs = [xmlfile] + deps,
    visibility = ["//visibility:public"],
  )
