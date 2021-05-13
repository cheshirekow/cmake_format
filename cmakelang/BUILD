load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
  name = "common",
  srcs = [
    "__init__.py",
    "common.py",
    "config_util.py",
    "configuration.py",
    "markup.py",
  ],
)

py_library(
  name = "cmakelang",
  srcs = [
    "annotate.py",
    "ctest_to.py",
    "genparsers.py",
    "markup_tests.py",
    "pypi/setup.py",
    "render.py",
    "tests.py",
    "tools/__init__.py",
    "tools/parse_cmake_help.py",
    "tools/properties.jinja.py",
    "tools/usage_lexer.py",
    "tools/usage_parser.py",
    "tools/variables.jinja.py",
  ],
  deps = [
    "//cmakelang/format",
    "//cmakelang/lex",
    "//cmakelang/parse",
    requirement("six"),
  ],
)

# -- Python 2 --

py_test(
  name = "markup_tests",
  srcs = ["markup_tests.py"],
  python_version = "PY2",
  deps = [":cmakelang"],
)

# -- Python 3 --

py_test(
  name = "markup_tests_py3",
  srcs = ["markup_tests.py"],
  main = "markup_tests.py",
  python_version = "PY3",
  deps = [":cmakelang"],
)
