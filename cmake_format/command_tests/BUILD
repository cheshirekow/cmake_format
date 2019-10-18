package(default_visibility=["//visibility:public"])

py_library(
    name="command_tests",
    srcs=[
        "__init__.py",
        "add_custom_command_tests.py",
        "add_executable_tests.py",
        "add_library_tests.py",
        "conditional_tests.py",
        "export_tests.py",
        "file_tests.py",
        "install_tests.py",
        "misc_tests.py",
        "set_tests.py"],
    data=[
        "add_custom_command_tests.cmake",
        "add_executable_tests.cmake",
        "add_library_tests.cmake",
        "conditional_tests.cmake",
        "export_tests.cmake",
        "file_tests.cmake",
        "install_tests.cmake",
        "misc_tests.cmake",
        "set_tests.cmake"])

# -- Python 2 --

py_test(
    name="add_custom_command_tests",
    srcs=["add_custom_command_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="add_executable_tests",
    srcs=["add_executable_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="add_library_tests",
    srcs=["add_library_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="conditional_tests",
    srcs=["conditional_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="export_tests",
    srcs=["export_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="file_tests",
    srcs=["file_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="install_tests",
    srcs=["install_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="misc_tests",
    srcs=["misc_tests.py"],
    deps=[
        "//cmake_format:cmake_format",
        "//cmake_format/test:data",
        ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="set_tests",
    srcs=["set_tests.py"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

# -- Python 3 --

py_test(
    name="add_custom_command_tests_py3",
    srcs=["add_custom_command_tests.py"],
    main="add_custom_command_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="add_executable_tests_py3",
    srcs=["add_executable_tests.py"],
    main="add_executable_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="add_library_tests_py3",
    srcs=["add_library_tests.py"],
    main="add_library_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="conditional_tests_py3",
    srcs=["conditional_tests.py"],
    main="conditional_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="export_tests_py3",
    srcs=["export_tests.py"],
    main="export_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="file_tests_py3",
    srcs=["file_tests.py"],
    main="file_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="install_tests_py3",
    srcs=["install_tests.py"],
    main="install_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="misc_tests_py3",
    srcs=["misc_tests.py"],
    main="misc_tests.py",
    deps=[
        "//cmake_format:cmake_format",
        "//cmake_format/test:data",
        ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="set_tests_py3",
    srcs=["set_tests.py"],
    main="set_tests.py",
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )