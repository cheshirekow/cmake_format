package(default_visibility = ["//visibility:public"])

py_library(
  name = "command_tests",
  srcs = [
    "__init__.py",
    "add_executable_tests.py",
    "add_library_tests.py",
    "misc_tests.py",
  ],
  data = [
    "add_custom_command_tests.cmake",
    "add_executable_tests.cmake",
    "add_library_tests.cmake",
    "conditional_tests.cmake",
    "export_tests.cmake",
    "external_project_tests.cmake",
    "file_tests.cmake",
    "foreach_tests.cmake",
    "install_tests.cmake",
    "misc_tests.cmake",
    "set_target_properties_tests.cmake",
    "set_tests.cmake",
  ],
)

# -- Python 2 --

py_test(
  name = "add_custom_command_tests",
  srcs = ["__main__.py"],
  args = ["TestAddCustomCommand"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "add_executable_tests",
  srcs = ["__main__.py"],
  args = ["TestAddExecutableCommand"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "add_library_tests",
  srcs = ["__main__.py"],
  args = ["TestAddLibraryCommand"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "conditional_tests",
  srcs = ["__main__.py"],
  args = ["TestConditional"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "export_tests",
  srcs = ["__main__.py"],
  args = ["TestExport"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "file_tests",
  srcs = ["__main__.py"],
  args = ["TestFile"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "install_tests",
  srcs = ["__main__.py"],
  args = ["TestInstall"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "misc_tests",
  srcs = ["__main__.py"],
  args = ["TestMiscFormatting"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
    "//cmake_format/test:data",
  ],
)

py_test(
  name = "set_target_properties",
  srcs = ["__main__.py"],
  args = ["TestSetTargetProperties"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "set_tests",
  srcs = ["__main__.py"],
  args = ["TestSet"],
  main = "__main__.py",
  python_version = "PY2",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

# -- Python 3 --

py_test(
  name = "add_custom_command_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestAddCustomCommand"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "add_executable_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestAddExecutableCommand"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "add_library_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestAddLibraryCommand"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "conditional_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestConditional"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "export_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestExport"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "file_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestFile"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "install_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestInstall"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "misc_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestMiscFormatting"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
    "//cmake_format/test:data",
  ],
)

py_test(
  name = "set_target_properties_py3",
  srcs = ["__main__.py"],
  args = ["TestSetTargetProperties"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)

py_test(
  name = "set_tests_py3",
  srcs = ["__main__.py"],
  args = ["TestSet"],
  main = "__main__.py",
  python_version = "PY3",
  deps = [
    ":command_tests",
    "//cmake_format",
  ],
)
