package(default_visibility = ["//visibility:public"])

py_library(
  name = "contrib_tests",
  srcs = [
    "__init__.py",
    "validate_pullrequest.py",
  ],
  data = [
    "signature_db.json",
  ],
)

# -- Python 2 --

py_test(
  name = "validate_pullrequest",
  srcs = ["validate_pullrequest.py"],
  python_version = "PY2",
  deps = [
    ":contrib_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "validate_database",
  srcs = ["validate_database.py"],
  python_version = "PY2",
  deps = [
    ":contrib_tests",
    "//cmake_format",
  ],
)

# -- Python 3 --

py_test(
  name = "validate_pullrequest_py3",
  srcs = ["validate_pullrequest.py"],
  main = "validate_pullrequest.py",
  python_version = "PY3",
  deps = [
    ":contrib_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "validate_database_py3",
  timeout = "long",
  srcs = ["validate_database.py"],
  main = "validate_database.py",
  python_version = "PY3",
  deps = [
    ":contrib_tests",
    "//cmake_format",
  ],
)
