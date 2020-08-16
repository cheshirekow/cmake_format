package(default_visibility = ["//visibility:public"])

py_library(
  name = "test",
  srcs = [
    "__init__.py",
    "command_db_test.py",
    "screw_users_test.py",
    "version_number_test.py",
  ],
)

# -- Python 2 --

py_test(
  name = "version_number_test",
  srcs = ["version_number_test.py"],
  python_version = "PY2",
  deps = [":test"],
)

py_test(
  name = "command_db_test",
  srcs = ["command_db_test.py"],
  python_version = "PY2",
  deps = [
    ":test",
    "//cmakelang",
  ],
)

# -- Python 3 --

py_test(
  name = "version_number_test_py3",
  srcs = ["version_number_test.py"],
  main = "version_number_test.py",
  python_version = "PY3",
  deps = [":test"],
)

py_test(
  name = "command_db_test_py3",
  srcs = ["command_db_test.py"],
  main = "command_db_test.py",
  python_version = "PY3",
  deps = [
    ":test",
    "//cmakelang",
  ],
)
