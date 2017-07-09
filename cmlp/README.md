cmakelists\_parsing
===================

Python module for parsing CMakeLists.txt files.

Installing
----------

    python setup.py install

or

    sudo pip install cmakelists_parsing

Usage
-----

The API can be used as follows:

    >>> import cmakelists_parsing.parsing as cmp
    >>> cmakelists_contents = 'FIND_PACKAGE(ITK REQUIRED)  # Hello, CMake!'
    >>> cmp.parse(cmakelists_contents)
    File([Command([u'ITK', u'REQUIRED', u'# Hello, CMake!'])])

There is also a command line utility called cmake_pprint that pretty-prints
CMake files:

    $ cmake_pprint CMakeLists.txt
