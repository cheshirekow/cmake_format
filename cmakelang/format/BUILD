load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
  name = "format",
  srcs = [
    "__init__.py",
    "__main__.py",
    "formatter.py",
  ],
  deps = [
    "//cmakelang:common",
  ],
)

py_library(
  name = "testdata",
  data = glob(["testdata/*"]),
)

# -- Python 2 --

py_binary(
  name = "cmake-format",
  srcs = ["__main__.py"],
  main = "__main__.py",
  deps = [":format"],
)

py_test(
  name = "invocation_tests",
  srcs = ["invocation_tests.py"],
  python_version = "PY2",
  deps = [
    ":testdata",
    "//cmakelang",
  ],
)

py_test(
  name = "layout_tests",
  srcs = ["layout_tests.py"],
  python_version = "PY2",
  deps = ["//cmakelang"],
)

# -- Python 3 --

py_test(
  name = "invocation_tests_py3",
  srcs = ["invocation_tests.py"],
  main = "invocation_tests.py",
  python_version = "PY3",
  deps = [
    ":testdata",
    "//cmakelang",
    requirement("six"),
  ],
)

py_test(
  name = "layout_tests_py3",
  srcs = ["layout_tests.py"],
  main = "layout_tests.py",
  python_version = "PY3",
  deps = [
    "//cmakelang",
  ],
)
