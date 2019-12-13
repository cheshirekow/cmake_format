package(default_visibility=["//visibility:public"])

py_library(
    name="cmake_lint",
    srcs=[
        "__init__.py",
        "__main__.py",
        "basic_checker.py",
        "lint_util.py",
        "lintdb.py"],
    deps=["//cmake_format:cmake_format"])

py_binary(
    name="cmake-lint",
    srcs=["__main__.py"],
    deps=[":cmake_lint"],
    main="__main__.py"
)
