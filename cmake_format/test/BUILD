package(default_visibility=["//visibility:public"])

py_library(
    name="test",
    srcs=[
        "__init__.py",
        "screw_users_test.py",
        "version_number_test.py"],
)

py_library(
    name="data",
    data=glob(["*"])
)

# -- Python 2 --

py_test(
    name="version_number_test",
    srcs=["version_number_test.py"],
    deps=[":test"],
    python_version="PY2",
    )

# -- Python 3 --

py_test(
    name="version_number_test_py3",
    srcs=["version_number_test.py"],
    main="version_number_test.py",
    deps=[":test"],
    python_version="PY3",
    )
