package(default_visibility=["//visibility:public"])

py_library(
    name="command_tests",
    srcs=[
        "__init__.py",
        "add_executable_tests.py",
        "add_library_tests.py",
        "misc_tests.py",
    ],
    data=[
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
    ])

# -- Python 2 --

py_test(
    name="add_custom_command_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddCustomCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="add_executable_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddExecutableCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="add_library_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddLibraryCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="conditional_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestConditional"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="export_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestExport"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="file_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestFile"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="install_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestInstall"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="misc_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestMiscFormatting"],
    deps=[
        "//cmake_format:cmake_format",
        "//cmake_format/test:data",
        ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="set_target_properties",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestSetTargetProperties"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

py_test(
    name="set_tests",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestSet"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY2",
    )

# -- Python 3 --

py_test(
    name="add_custom_command_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddCustomCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="add_executable_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddExecutableCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="add_library_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestAddLibraryCommand"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="conditional_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestConditional"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="export_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestExport"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="file_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestFile"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="install_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestInstall"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="misc_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestMiscFormatting"],
    deps=[
        "//cmake_format:cmake_format",
        "//cmake_format/test:data",
        ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="set_target_properties_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestSetTargetProperties"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )

py_test(
    name="set_tests_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    args=["TestSet"],
    deps=["//cmake_format:cmake_format", ":command_tests"],
    python_version="PY3",
    )
