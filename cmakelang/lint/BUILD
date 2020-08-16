package(default_visibility = ["//visibility:public"])

py_library(
  name = "lint",
  srcs = [
    "__init__.py",
    "__main__.py",
    "basic_checker.py",
    "gendocs.py",
    "lint_util.py",
    "lintdb.py",
  ],
  deps = ["//cmakelang"],
)

py_binary(
  name = "cmake-lint",
  srcs = ["__main__.py"],
  main = "__main__.py",
  deps = [":lint"],
)
