package(default_visibility = ["//visibility:public"])

py_library(
  name = "lex",
  srcs = [
    "__init__.py",
    "__main__.py",
  ],
  deps = ["//cmakelang:common"],
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
