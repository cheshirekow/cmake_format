load("@rules_cc//cc:defs.bzl", "cc_library")
load("@rules_python//python:defs.bzl", "py_runtime", "py_runtime_pair")

filegroup(
  name = "lsb-release",
  srcs = ["etc/lsb-release"],
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
  name = "libpng16",
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libpng16.a",
    "usr/lib/x86_64-linux-gnu/libpng16.so",
  ],
  hdrs = glob(["usr/include/libpng16/*.h"]),
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
  deps = [":zlib"],
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
  deps = [":libpng16", ":zlib"],
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
  srcs = ["lib/x86_64-linux-gnu/libudev.so"],
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

cc_library(
  name = "tinyxml2",
  includes = ["usr/include"],
  hdrs = ["usr/include/tinyxml2.h"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libtinyxml2.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libresolv",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libresolv.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libselinux",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libselinux.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libmount",
  srcs = glob(["lib/x86_64-linux-gnu/libmount.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libffi",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libffi.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "graphite2",
  includes = ["usr/include"],
  hdrs = glob(["usr/include/graphite2/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgraphite2.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libpcre",
  includes = ["usr/include"],
  hdrs = glob(["usr/include/pcre.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpcre.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libthai",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libthai.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libloki",
  hdrs = glob([
    "usr/include/loki/*",
    "usr/include/loki/flex/*",
    "usr/include/loki/yasli/*",
  ]),
  srcs = glob([
    "usr/lib/libloki.so.0.1.7",
    "usr/lib/libloki.so",
    "usr/lib/libloki.a",
  ]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libelf",
  hdrs = ["usr/include/elf.h", "usr/include/libelf.h"],
  srcs = glob(["usr/lib/x86_64-linux-gnu/libelf.*"]),
  visibility = ["//visibility:public"],
)

# ---------------
# GNOME libraries
# ---------------

cc_library(
  name = "atk-1.0",
  includes = [
    "usr/include/atk-1.0",
  ],
  hdrs = glob(["usr/include/atk-1.0/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libatk-1.0.*"]),
  deps = [":gobject-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "at-spi-2.0",
  includes = ["usr/include/at-spi-2.0"],
  hdrs = glob(["usr/include/at-spi-2.0/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libatspi.*"]),
  deps = [":dbus-1", ":glib-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "cairo",
  includes = ["usr/include/cairo"],
  hdrs = glob(["usr/include/cairo/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libcairo.*"]),
  deps = [":freetype2", "glib-2.0", ":libpng16", ":pixman-1", ":libX11"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "cairo-gobject",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libcairo-gobject.*"]),
  deps = [":cairo", "glib-2.0", ":gobject-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "dbus-1",
  includes = [
    "usr/include/dbus-1.0",
    "usr/lib/x86_64-linux-gnu/dbus-1.0/include",
  ],
  hdrs = glob([
    "usr/include/dbus-1.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/dbus-1.0/include/**/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libdbus-1.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gdk-3.0",
  includes = ["usr/include/gtk-3.0"],
  hdrs = glob(["usr/include/gtk-3.0/gdk/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgdk-3*"]),
  linkopts = ["-pthread"],
  deps = [
    ":cairo",
    ":cairo-gobject",
    ":gdk-pixbuf-2.0",
    ":pango-1.0",
    ":pangocairo-1.0",
    ":pangoft2-1.0",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gdk-pixbuf-2.0",
  includes = ["usr/include/gdk-pixbuf-2.0"],
  hdrs = glob(["usr/include/gdk-pixbuf-2.0/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgdk-pixbuf-2.0.*"]),
  deps = [":gobject-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gio-2.0",
  includes = ["usr/include/gio-unix-2.0"],
  hdrs = glob(["usr/include/gio-unix-2.0/**/*.h"]),
  srcs = glob([
    "usr/lib/x86_64-linux-gnu/libgio-2.0.*",
    "usr/lib/x86_64-linux-gnu/gio/modules/*.so",
  ]),
  deps = [
    ":glib-2.0",
    ":gmodule-2.0",
    ":gobject-2.0",
    ":libmount",
    ":libresolv",
    ":libselinux",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "glib-2.0",
  includes = [
    "usr/include/glib-2.0",
    "usr/lib/x86_64-linux-gnu/glib-2.0/include",
  ],
  hdrs = glob([
    "usr/include/glib-2.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/glib-2.0/include/glibconfig.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libglib-2.0*"]),
  deps = ["libpcre"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gmodule-2.0",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgmodule-2.0.*"]),
  deps = [":dl", ":glib-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gobject-2.0",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgobject-2.0*"]),
  deps = [":glib-2.0", ":libffi"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gtk-3.0",
  includes = ["usr/include/gtk-3.0"],
  hdrs = glob(["usr/include/gtk-3.0/gtk/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgtk-3*"]),
  deps = [
    ":atk-1.0",
    ":cairo",
    ":cairo-gobject",
    ":gdk-3.0",
    ":gdk-pixbuf-2.0",
    "gio-2.0",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gtk-unix-print-3.0",
  includes = ["usr/include/gtk-3.0"],
  hdrs = glob(["usr/include/gtk-3.0/unix-print/gtk/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgtk-3*"]),
  deps = [
    ":atk-1.0",
    ":cairo",
    ":cairo-gobject",
    ":gdk-pixbuf-2.0",
    ":gio-2.0",
    "gtk-3.0",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "harfbuzz",
  includes = ["usr/include/harfbuzz"],
  hdrs = glob(["usr/include/harfbuzz/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libharfbuzz.*"]),
  deps = [":glib-2.0", ":graphite2"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "pango-1.0",
  includes = ["usr/include/pango-1.0"],
  hdrs = glob(["usr/include/pango-1.0/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpango-1.0.*"]),
  deps = [":glib-2.0", ":gobject-2.0", ":libthai"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "pangoft2-1.0",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpangoft2-1.0.*"]),
  deps = [":pango-1.0", ":freetype2", ":fontconfig"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "pangocairo-1.0",
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpangocairo-1.0.*"]),
  deps = [
    ":cairo",
    ":fontconfig",
    ":freetype2",
    ":glib-2.0",
    ":harfbuzz",
    ":libpng16",
    ":pango-1.0",
    ":pixman-1",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "pixman-1",
  includes = ["usr/include/pixman-1"],
  hdrs = glob(["usr/include/pixman-1/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpixman-1.*"]),
  visibility = ["//visibility:public"],
)

# ------------------------------
# GNOME libraries - C++ bindings
# ------------------------------

cc_library(
  name = "atkmm-1.6",
  includes = ["usr/include/atkmm-1.6"],
  hdrs = glob(["usr/include/atkmm-1.6/**/*.h"]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libatkmm-1.6.*"]),
  deps = [":atk-1.0", ":glibmm-2.4"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "cairomm-1.0",
  includes = [
    "usr/include/cairomm-1.0",
    "usr/lib/x86_64-linux-gnu/cairomm-1.0/include",
  ],
  hdrs = glob([
    "usr/include/cairomm-1.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/cairomm-1.0/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libcairomm-1.0.*"]),
  deps = [":cairo", ":sigc++-2.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "gdkmm-3.0",
  includes = [
    "usr/include/gdkmm-3.0",
    "usr/lib/x86_64-linux-gnu/gdkmm-3.0/include",
  ],
  hdrs = glob([
    "usr/include/gdkmm-3.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/gdkmm-3.0/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgdkmm-3.0.*"]),
  deps = [
    "cairomm-1.0",
    "gdk-pixbuf-2.0",
    "giomm-2.4",
    "gtk-3.0",
    "pangomm-1.4",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "giomm-2.4",
  includes = [
    "usr/include/giomm-2.4",
    "usr/lib/x86_64-linux-gnu/giomm-2.4/include",
  ],
  hdrs = glob([
    "usr/include/giomm-2.4/**/*.h",
    "usr/lib/x86_64-linux-gnu/giomm-2.4/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgiomm-2.4.*"]),
  deps = [":gio-2.0", "glibmm-2.4"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "glibmm-2.4",
  includes = [
    "usr/include/glibmm-2.4",
    "usr/lib/x86_64-linux-gnu/glibmm-2.4/include",
  ],
  hdrs = glob([
    "usr/include/glibmm-2.4/**/*.h",
    "usr/lib/x86_64-linux-gnu/glibmm-2.4/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libglibmm-2.4.*"]),
  visibility = ["//visibility:public"],
)

filegroup(
  name = "glibmm-2.4-m4",
  srcs = glob(["usr/lib/x86_64-linux-gnu/glibmm-2.4/proc/m4/*"]),
)

filegroup(
  name = "atkmm-1.6-m4",
  srcs = glob(["usr/lib/x86_64-linux-gnu/atkmm-1.6/proc/m4/*"]),
)

filegroup(
  name = "pangomm-1.4-m4",
  srcs = glob(["usr/lib/x86_64-linux-gnu/pangomm-1.4/proc/m4/*"]),
)

filegroup(
  name = "gtkmm-3.0-m4",
  srcs = glob(["usr/lib/x86_64-linux-gnu/gtkmm-3.0/proc/m4/*"]),
)

filegroup(
  name = "glibmm-2.4-pm",
  srcs = glob(["usr/lib/x86_64-linux-gnu/glibmm-2.4/proc/pm/*"]),
)

sh_binary(
  name = "gmmproc",
  srcs = ["usr/lib/x86_64-linux-gnu/glibmm-2.4/proc/gmmproc"],
  data = [
    ":glibmm-2.5-m4",
    ":glibmm-2.5-pm",
    ":atkmm-1.6-m4",
    ":pangomm-1.4-m4",
    ":gtkmm-3.0-m5",
  ],
)

sh_binary(
  name = "gmmproc-generate_wrap_init",
  srcs = [
    "usr/lib/x86_64-linux-gnu/glibmm-2.4/proc/generate_wrap_init.pl",
  ],
)

cc_library(
  name = "gtkmm-3.0",
  includes = [
    "usr/include/gtkmm-3.0",
    "usr/lib/x86_64-linux-gnu/gtkmm-3.0/include",
  ],
  hdrs = glob([
    "usr/include/gtkmm-3.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/gtkmm-3.0/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libgtkmm-3.0.*"]),
  deps = [
    ":atkmm-1.6",
    ":cairomm-1.0",
    ":gdkmm-3.0",
    ":gdk-pixbuf-2.0",
    ":giomm-2.4",
    ":gtk-3.0",
    ":gtk-unix-print-3.0",
    ":pangomm-1.4",
  ],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "pangomm-1.4",
  includes = [
    "usr/include/pangomm-1.4",
    "usr/lib/x86_64-linux-gnu/pangomm-1.4/include",
  ],
  hdrs = glob([
    "usr/include/pangomm-1.4/**/*.h",
    "usr/lib/x86_64-linux-gnu/pangomm-1.4/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libpangomm-1.4.*"]),
  deps = [":cairomm-1.0", ":glibmm-2.4", ":pangocairo-1.0"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "sigc++-2.0",
  includes = [
    "usr/include/sigc++-2.0",
    "usr/lib/x86_64-linux-gnu/sigc++-2.0/include",
  ],
  hdrs = glob([
    "usr/include/sigc++-2.0/**/*.h",
    "usr/lib/x86_64-linux-gnu/sigc++-2.0/include/*.h",
  ]),
  srcs = glob(["usr/lib/x86_64-linux-gnu/libsigc-2.0.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "re2",
  hdrs = glob([
    "usr/include/re2/*.h",
  ]),
  # NOTE(josh): libre2.so is missing operator<< for stringpiece
  srcs = ["usr/lib/x86_64-linux-gnu/libre2.a"],
  visibility = ["//visibility:public"],
  linkopts = ["-pthread"],
)

cc_library(
  name = "fmt",
  hdrs = glob([
    "usr/include/fmt/*.h",
  ]),
  srcs = glob(["usr/lib/libfmt.*"]),
  visibility = ["//visibility:public"],
)

cc_library(
  name = "python-dev",
  srcs = [
    "usr/lib/python3.6/config-3.6m-x86_64-linux-gnu/libpython3.6.so",
    "usr/lib/x86_64-linux-gnu/libpython3.6m.so.1.0",
    "usr/lib/x86_64-linux-gnu/libpython3.6m.so.1",
  ],
  hdrs = glob(["usr/include/python3.6m/*.h"]),
  includes = ["usr/include/python3.6m"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libllvm",
  srcs = [
    "usr/lib/llvm-8/lib/libLLVM.so",
    "usr/lib/llvm-8/lib/libLLVM-8.so",
  ],
  hdrs = glob(["usr/lib/llvm-8/include/llvm-c/*.h"]),
  includes = ["usr/lib/llvm-8/include"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libclang",
  srcs = [
    "usr/lib/llvm-8/lib/libclang-8.0.0.so",
    "usr/lib/llvm-8/lib/libclang-8.so",
    "usr/lib/llvm-8/lib/libclang-8.so.1",
    "usr/lib/x86_64-linux-gnu/libclang-8.so",
    "usr/lib/x86_64-linux-gnu/libclang-8.so.1",
  ],
  deps = ["libllvm"],
  hdrs = glob(["usr/lib/llvm-8/include/clang-c/*.h"]),
  includes = ["usr/lib/llvm-8/include"],
  visibility = ["//visibility:public"],
)

py_runtime(
  name = "python-3.6.6",
  files = glob(["usr/lib/python3.6/*"]),
  interpreter = "usr/bin/python3.6",
  python_version = "PY3",
)

py_runtime(
  name = "python-2.7.17",
  files = glob(["usr/lib/python2.7/*"]),
  interpreter = "usr/bin/python2.7",
  python_version = "PY2",
)

py_runtime_pair(
  name = "py_runtime",
  py2_runtime = ":python-2.7.17",
  py3_runtime = ":python-3.6.6",
)

cc_library(
  name = "libzip-config",
  hdrs = [
    "usr/lib/x86_64-linux-gnu/libzip/include/zipconf.h",
  ],
  strip_include_prefix = "usr/lib/x86_64-linux-gnu/libzip/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libzip",
  srcs = [
    "usr/lib/x86_64-linux-gnu/libzip.so.4",
    "usr/lib/x86_64-linux-gnu/libzip.so",
    "usr/lib/x86_64-linux-gnu/libzip.so.4.0.0",
    "usr/lib/x86_64-linux-gnu/libzip.a",
  ],
  hdrs = [
    "usr/include/zip.h",
  ],
  deps = [":zlib", ":libzip-config"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libuuid",
  srcs = [
    "usr/lib/x86_64-linux-gnu/libuuid.so",
    "usr/lib/x86_64-linux-gnu/libuuid.a",
  ],
  hdrs = ["usr/include/uuid/uuid.h"],
  strip_include_prefix = "usr/include",
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libpng",
  deps = [":libpng16"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libcrypto",
  hdrs = [],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0",
    "usr/lib/x86_64-linux-gnu/libcrypto.so.1.1",
    "usr/lib/x86_64-linux-gnu/libcrypto.a",
    "usr/lib/x86_64-linux-gnu/libcrypto.so",
  ],
  includes = ["usr/include"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libssl",
  hdrs = [],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libssl.so.1.0.0",
    "usr/lib/x86_64-linux-gnu/libssl3.so",
    "usr/lib/x86_64-linux-gnu/libssl.so",
    "usr/lib/x86_64-linux-gnu/libssl.so.1.1",
    "usr/lib/x86_64-linux-gnu/libssl.a",
  ],
  includes = ["usr/include"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libgssapi",
  srcs = [
    "usr/lib/x86_64-linux-gnu/libgssapi.so.3",
    "usr/lib/x86_64-linux-gnu/libgssapi.so.3.0.0",
    "usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2",
    "usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2",
  ],
  includes = ["usr/include"],
  visibility = ["//visibility:public"],
)

cc_library(
  name = "libssh",
  hdrs = [
    "usr/include/libssh/legacy.h",
    "usr/include/libssh/libssh.h",
    "usr/include/libssh/libsshpp.hpp",
    "usr/include/libssh/server.h",
    "usr/include/libssh/sftp.h",
    "usr/include/libssh/ssh2.h",
  ],
  includes = ["usr/include"],
  visibility = ["//visibility:public"],
  deps = [":libcrypto", ":libssl", ":libgssapi"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libssh.so.4.5.0",
    "usr/lib/x86_64-linux-gnu/libssh.so.4",
    "usr/lib/x86_64-linux-gnu/libssh.so",
    "usr/lib/x86_64-linux-gnu/libssh.a",
  ],
)

cc_library(
  name = "libssh_threads",
  hdrs = ["usr/include/libssh/callbacks.h"],
  visibility = ["//visibility:public"],
  includes = ["usr/include"],
  srcs = [
    "usr/lib/x86_64-linux-gnu/libssh_threads.so.4.5.0",
    "usr/lib/x86_64-linux-gnu/libssh_threads.so.4",
    "usr/lib/x86_64-linux-gnu/libssh_threads.a",
    "usr/lib/x86_64-linux-gnu/libssh_threads.so",
  ],
)

cc_library(
  name = "librsvg-2.0",
  includes = ["usr/include/librsvg-2.0"],
  visibility = ["//visibility:public"],
  hdrs = [
    "usr/include/librsvg-2.0/librsvg/rsvg.h",
    "usr/include/librsvg-2.0/librsvg/librsvg-enum-types.h",
    "usr/include/librsvg-2.0/librsvg/librsvg-features.h",
    "usr/include/librsvg-2.0/librsvg/rsvg-cairo.h",
  ],
  srcs = [
    "usr/lib/x86_64-linux-gnu/librsvg-2.so.2.40.20",
    "usr/lib/x86_64-linux-gnu/librsvg-2.so.2",
    "usr/lib/x86_64-linux-gnu/librsvg-2.so",
  ],
)
