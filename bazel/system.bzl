config_setting(
  name = "xenial_amd64",
  define_values = {"suite": "xenial"},
)

config_setting(
  name = "bionic_amd64",
  define_values = {"suite": "bionic"},
)

cc_library(
  name = "dl",
  includes = ["usr/include"],
  srcs = [
    # NOTE(josh): linking to libdl.a is unusual, but is the default
    # if we allow this into the sandbox
    # "usr/lib/x86_64-linux-gnu/libdl.a",
    "usr/lib/x86_64-linux-gnu/libdl.so",
  ],
  hdrs = ["usr/include/dlfcn.h"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "eigen3",
  includes = ["usr/include/eigen3"],
  srcs = [],
  hdrs = glob(["usr/include/eigen3/**"]),
  strip_include_prefix = "usr/include/eigen3",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libunwind",
  srcs = ["usr/lib/x86_64-linux-gnu/libunwind.so.8"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libgflags",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libgflags.a",
    "usr/lib/x86_64-linux-gnu/libgflags.so",
  ],
  hdrs = glob(["usr/include/gflags/**"]),
  # NOTE(josh): libunwind only needed for static link
  deps = [":libunwind"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "glog",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libglog.a",
    "usr/lib/x86_64-linux-gnu/libglog.so",
  ],
  deps = [":libgflags"],
  hdrs = glob(["usr/include/glog/**"]),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "expat",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libexpat.a",
    "usr/lib/x86_64-linux-gnu/libexpat.so",
  ],
  hdrs = ["usr/include/expat.h"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libpng",
  includes = ["usr/include"],
  srcs = select({
    ":xenial_amd64": [
      "usr/lib/x86_64-linux-gnu/libpng12.a",
      "usr/lib/x86_64-linux-gnu/libpng12.so",
    ],
    "bionic_amd64": [
      "usr/lib/x86_64-linux-gnu/libpng16.a",
      "usr/lib/x86_64-linux-gnu/libpng16.so",
    ],
  }),
  hdrs = select({
    ":xenial_amd64": glob(["usr/include/libpng12/*.h"]),
    ":bionic_amd64": glob(["usr/include/libpng16/*.h"]),
  }),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "zlib",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libz.a",
    "usr/lib/x86_64-linux-gnu/libz.so",
  ],
  hdrs = ["usr/include/zconf.h", "usr/include/zlib.h"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "freetype2",
  includes = ["usr/include/freetype2"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libfreetype.a",
    "usr/lib/x86_64-linux-gnu/libfreetype.so",
  ],
  hdrs = glob(["usr/include/freetype2/**"]),
  deps = [":libpng", ":zlib"],
  strip_include_prefix = "usr/include/freetype2",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "fontconfig",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libfontconfig.a",
    "usr/lib/x86_64-linux-gnu/libfontconfig.so",
  ],
  hdrs = glob(["usr/include/fontconfig/**"]),
  deps = [":expat", ":freetype2", ":zlib"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "fuse",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libfuse.a",
    "usr/lib/x86_64-linux-gnu/libfuse.so",
  ],
  hdrs = glob(["usr/include/fuse/**"]),
  deps = [":dl"],
  defines = ["_FILE_OFFSET_BITS=64"],
  linkopts = ["-pthread"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libidn",
  srcs = ["usr/lib/x86_64-linux-gnu/libcidn.so"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "librtmp",
  srcs = ["usr/lib/x86_64-linux-gnu/librtmp.so.1"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libcurl",
  includes = ["usr/include"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libcurl*.so"]),
  hdrs = glob(["usr/include/curl/**"]),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

# NOTE(josh): if you want to link libcurl static, you need all this other
# stuff.
# cc_library(
#     name = "libcurl",
#     includes =["usr/include"],
#     srcs = glob(["usr/lib/x86_64-linux-gnu/libcurl*"]),
#     hdrs = glob(["usr/include/curl/**"]),
#     deps = [":libidn", ":librtmp", ":libssl",
#             ":libcrypto", ":libgssapi_krb4",
#             ":libkrb5", ":libk5crypto", ":libcom_err",
#             "liblber", "libldap", ":zlib"],
#     defines = ["_FILE_OFFSET_BITS=64"],
#     linkopts = ["-z,relro", "-Bsymbolic-functions"],
#     strip_include_prefix="usr/include",
#     visibility = ["//visibility:public"],
# )

cc_library(
  name = "libudev",
  includes = ["usr/include"],
  srcs = select({
    ":xenial_amd64": ["usr/lib/x86_64-linux-gnu/libudev.so"],
    ":bionic_amd64": ["lib/x86_64-linux-gnu/libudev.so"],
  }),
  hdrs = ["usr/include/libudev.h"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_binary(
  name = "glslang",
  srcs = ["bin/glslangValidator"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libvulkan",
  includes = ["usr/include"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libvulkan.so"]),
  hdrs = glob(["usr/include/vulkan/**"]),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libX11",
  includes = ["usr/include"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libX*.so"]),
  hdrs = glob(["usr/include/X11/**"]),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libxcb",
  includes = ["usr/include"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libxcb*.so"]),
  hdrs = glob(["usr/include/xcb/**"]),
  deps = [":libX11"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)
