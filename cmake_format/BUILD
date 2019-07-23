package(default_visibility=["//visibility:public"])

py_library(
    name="cmake_format",
    srcs=[
        "doc/gendoc_sources.py",
        "doc/conf.py",
        "screw_users_test.py",
        "__main__.py",
        "parser_tests.py",
        "common.py",
        "markup_tests.py",
        "format_tests.py",
        "layout_tests.py",
        "invocation_tests.py",
        "__init__.py",
        "formatter.py",
        "configuration.py",
        "command_tests/file_tests.py",
        "command_tests/add_library_tests.py",
        "command_tests/install_tests.py",
        "command_tests/add_executable_tests.py",
        "command_tests/__init__.py",
        "command_tests/export_tests.py",
        "command_tests/conditional_tests.py",
        "command_tests/set_tests.py",
        "command_tests/add_custom_command_tests.py",
        "parse_funs/external_project.py",
        "parse_funs/file.py",
        "parse_funs/add_library.py",
        "parse_funs/__init__.py",
        "parse_funs/add_executable.py",
        "parse_funs/add_xxx.py",
        "parse_funs/install.py",
        "parse_funs/fetch_content.py",
        "tests.py",
        "commands.py",
        "pypi/setup.py",
        "render.py",
        "parser.py",
        "lexer_tests.py",
        "test/cmake-format.py",
        "lexer.py",
        "annotate.py",
        "markup.py"],
    data=["templates/layout.html.tpl",
          "templates/style.css"])

py_binary(
    name="cmake-format",
    srcs=["__main__.py"],
    deps=[":cmake_format"],
    main="__main__.py"
)

py_test(
    name="format_tests",
    srcs=["format_tests.py"],
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    python_version="PY2",
    )

py_test(
    name="invocation_tests",
    srcs=["invocation_tests.py"],
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    python_version="PY2",
    )

py_test(
    name="layout_tests",
    srcs=["layout_tests.py"],
    deps=[":cmake_format"],
    python_version="PY2",
    )

py_test(
    name="lexer_tests",
    srcs=["lexer_tests.py"],
    deps=[":cmake_format"],
    python_version="PY2",
    )

py_test(
    name="markup_tests",
    srcs=["markup_tests.py"],
    deps=[":cmake_format"],
    python_version="PY2",
    )

py_test(
    name="parser_tests",
    srcs=["parser_tests.py"],
    deps=[":cmake_format"],
    python_version="PY2",
    )


py_test(
    name="format_tests_py3",
    srcs=["format_tests.py"],
    main="format_tests.py",
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    python_version="PY3",
    )

py_test(
    name="invocation_tests_py3",
    srcs=["invocation_tests.py"],
    main="invocation_tests.py",
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    python_version="PY3",
    )

py_test(
    name="layout_tests_py3",
    srcs=["layout_tests.py"],
    main="layout_tests.py",
    deps=[":cmake_format"],
    python_version="PY3",
    )

py_test(
    name="lexer_tests_py3",
    srcs=["lexer_tests.py"],
    main="lexer_tests.py",
    deps=[":cmake_format"],
    python_version="PY3",
    )

py_test(
    name="markup_tests_py3",
    srcs=["markup_tests.py"],
    main="markup_tests.py",
    deps=[":cmake_format"],
    python_version="PY3",
    )

py_test(
    name="parser_tests_py3",
    srcs=["parser_tests.py"],
    main="parser_tests.py",
    deps=[":cmake_format"],
    python_version="PY3",
    )
