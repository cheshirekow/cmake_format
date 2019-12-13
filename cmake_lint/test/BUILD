package(default_visibility=["//visibility:public"])

py_library(
    name="test",
    srcs=[
        "__init__.py",
        "__main__.py",
        "genfiles.py"],
)

py_library(
    name="data",
    data=glob(["*.cmake"])
)

# -- Python 2 --

py_test(
    name="lint_test",
    srcs=["__main__.py"],
    main="__main__.py",
    deps=["//cmake_lint:cmake_lint", ":test"],
    python_version="PY2",
)

# -- Python 3 --

py_test(
    name="lint_test_py3",
    srcs=["__main__.py"],
    main="__main__.py",
    deps=["//cmake_lint:cmake_lint", ":test"],
    python_version="PY3",
)
