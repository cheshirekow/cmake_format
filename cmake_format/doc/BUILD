package(default_visibility=["//visibility:public"])

py_library(
    name="doc_tests",
    srcs=[
        "__init__.py",
        "conf.py",
        "docsources_test.py",
        "gendoc_sources.py"],
    data=[])

# -- Python 2 --

py_test(
    name="docsources_test",
    srcs=["docsources_test.py"],
    deps=["//cmake_format:cmake_format", ":doc_tests"],
    python_version="PY2",
    )

# -- Python 3 --

py_test(
    name="docsources_test_py3",
    srcs=["docsources_test.py"],
    main="docsources_test.py",
    deps=["//cmake_format:cmake_format", ":doc_tests"],
    python_version="PY3",
    )
