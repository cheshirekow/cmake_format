load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
  name = "parse",
  srcs = [
    "__init__.py",
    "additional_nodes.py",
    "argument_nodes.py",
    "body_nodes.py",
    "common.py",
    "funs/__init__.py",
    "funs/add_executable.py",
    "funs/add_library.py",
    "funs/add_xxx.py",
    "funs/break.py",
    "funs/deprecated.py",
    "funs/external_project.py",
    "funs/fetch_content.py",
    "funs/file.py",
    "funs/foreach.py",
    "funs/install.py",
    "funs/list.py",
    "funs/miscellaneous.py",
    "funs/random.py",
    "funs/set.py",
    "funs/set_target_properties.py",
    "funs/standard_builtins.py",
    "funs/standard_funs.py",
    "funs/standard_modules.py",
    "printer.py",
    "properties.py",
    "simple_nodes.py",
    "statement_node.py",
    "util.py",
    "variables.py",
  ],
  deps = [
    "//cmakelang:common",
    requirement("six"),
  ],
)

# -- Python 2 --

py_test(
  name = "tests",
  srcs = ["tests.py"],
  python_version = "PY2",
  deps = ["//cmakelang"],
)

# -- Python 3 --

py_test(
  name = "tests_py3",
  srcs = ["tests.py"],
  main = "tests.py",
  python_version = "PY3",
  deps = ["//cmakelang"],
)
