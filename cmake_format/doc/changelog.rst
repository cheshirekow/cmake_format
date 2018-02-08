=========
Changelog
=========

------
v0.3.0
------

* fix `cheshirekow/cmake_format#2`_ : parser matching builtin logical expression
  names should not be case sensitive
* fix `cheshirekow/cmake_format#3`_ : default code used to read
  ``long_description`` can't decode utf8
* implement `cheshirekow/cmake_format#7`_ : add configuration option to separate
  control statement or function name from parenthesis
* implement `cheshirekow/cmake_format#9`_ : allow configuration options specified
  from command line
* Add support for python as the configfile format
* Add ``--dump-config`` option
* Add support for "separator" lines in comments. Any line consisting of only
  five or more non-alphanum characters will be preserved verbatim.
* Improve python3 support by using ``print_function``

.. _cheshirekow/cmake_format#2: https://github.com/cheshirekow/cmake_format/issues/2
.. _cheshirekow/cmake_format#3: https://github.com/cheshirekow/cmake_format/issues/3
.. _cheshirekow/cmake_format#7: https://github.com/cheshirekow/cmake_format/issues/7
.. _cheshirekow/cmake_format#9: https://github.com/cheshirekow/cmake_format/issues/9

------
v0.2.1
------

* fix bug in reflow if text goes to exactly the end of the line
* add python module documentation to sphinx autodoc
* make formatting of COMMANDs a bit more compact

------
v0.2.0
------

* add unit tests using python unit test framework
* accept configuration as yaml or json
* Implemented custom cmake AST parser, getting rid of dependency on cmlp
* Removed static global command configuration
* If no configuration file specified, search for a file based on the input
  file path.
* Moved code out of ``__main__.py`` and into modules
* More documentation and general cleanup
* Add ``setup.py``
* Tested on a production codebase with 350+ listfiles and a manual scan of
  changes looked good, and the build seems to be healthy.
