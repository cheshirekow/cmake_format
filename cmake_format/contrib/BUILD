package(default_visibility=["//visibility:public"])

py_library(
    name="contrib_tests",
    srcs=[
        "__init__.py",
        "validate_pullrequest.py"],
    data=[
        "signature_db.json"])

# -- Python 2 --

py_test(
    name="validate_pullrequest",
    srcs=["validate_pullrequest.py"],
    deps=["//cmake_format:cmake_format", ":contrib_tests"],
    python_version="PY2",
    )

py_test(
    name="validate_database",
    srcs=["validate_database.py"],
    deps=["//cmake_format:cmake_format", ":contrib_tests"],
    python_version="PY2",
    )

# -- Python 3 --

py_test(
    name="validate_pullrequest_py3",
    srcs=["validate_pullrequest.py"],
    main="validate_pullrequest.py",
    deps=["//cmake_format:cmake_format", ":contrib_tests"],
    python_version="PY3",
    )

py_test(
    name="validate_database_py3",
    srcs=["validate_database.py"],
    main="validate_database.py",
    deps=["//cmake_format:cmake_format", ":contrib_tests"],
    python_version="PY3",
    )
