package(default_visibility=["//visibility:public"])

py_library(
    name="cmake_format",
    srcs=["__init__.py",
          "__main__.py",
          "commands.py",
          "common.py",
          "configuration.py",
          "formatter.py",
          "lexer.py",
          "markup.py",
          "parser.py",
          "render.py"],
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
    default_python_version="PY2",
    #python_version="PY2",
    )

py_test(
    name="invocation_tests",
    srcs=["invocation_tests.py"],
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    default_python_version="PY2",
    #python_version="PY2",
    )

py_test(
    name="layout_tests",
    srcs=["layout_tests.py"],
    deps=[":cmake_format"],
    default_python_version="PY2",
    #python_version="PY2",
    )

py_test(
    name="lexer_tests",
    srcs=["lexer_tests.py"],
    deps=[":cmake_format"],
    default_python_version="PY2",
    #python_version="PY2",
    )

py_test(
    name="markup_tests",
    srcs=["markup_tests.py"],
    deps=[":cmake_format"],
    default_python_version="PY2",
    #python_version="PY2",
    )

py_test(
    name="parser_tests",
    srcs=["parser_tests.py"],
    deps=[":cmake_format"],
    default_python_version="PY2",
    #python_version="PY2",
    )


py_test(
    name="format_tests_py3",
    srcs=["format_tests.py"],
    main="format_tests.py",
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    default_python_version="PY3",
    #python_version="PY3",
    )

py_test(
    name="invocation_tests_py3",
    srcs=["invocation_tests.py"],
    main="invocation_tests.py",
    deps=[":cmake_format"],
    data=glob(["test/*"]),
    default_python_version="PY3",
    #python_version="PY3",
    )

py_test(
    name="layout_tests_py3",
    srcs=["layout_tests.py"],
    main="layout_tests.py",
    deps=[":cmake_format"],
    default_python_version="PY3",
    #python_version="PY3",
    )

py_test(
    name="lexer_tests_py3",
    srcs=["lexer_tests.py"],
    main="lexer_tests.py",
    deps=[":cmake_format"],
    default_python_version="PY3",
    #python_version="PY3",
    )

py_test(
    name="markup_tests_py3",
    srcs=["markup_tests.py"],
    main="markup_tests.py",
    deps=[":cmake_format"],
    default_python_version="PY3",
    #python_version="PY3",
    )

py_test(
    name="parser_tests_py3",
    srcs=["parser_tests.py"],
    main="parser_tests.py",
    deps=[":cmake_format"],
    default_python_version="PY3",
    #python_version="PY3",
    )
