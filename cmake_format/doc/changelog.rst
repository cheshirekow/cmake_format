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

v0.3.1
------

* use exec instead of execfile for python3 compatibility

v0.3.2
------

* Move configuration to it's own module
* Add lexer/parser support for bracket arguments and bracket comments
* Make stable_wrap work for any ``prefix``/``subsequent_prefix``.
* Preserve scope-level bracket comments verbatim
* Add markup module with parse/format support for rudimentary markup in comments
  including nested bulleted and enumerated lists, and fenced blocks.
* Add pyyaml as an extra dependency in pip configuration
* Fix `cheshirekow/cmake_format#16`_: argparse defaults always override config

v0.3.3
------

* Convert all string literals in format.py to unicode literals
* Added python3 tests
* Attempt to deal with python2/python3 string differences by using codecs
  and io modules where appropriate. I probably got this wrong somewhere.
* Fix missing comma in config file matching

* Implement `cheshirekow/cmake_format#13`_: option to dangle parenthesis
* Fix `cheshirekow/cmake_format#17`_: trailing comment stripped from commands
  with no arguments
* Fix `cheshirekow/cmake_format#21`_: corruption upon trailing whitespace
* Fix `cheshirekow/cmake_format#23`_: wrapping long arguments has some weird
  extra newline or missing indentation space.
* Fix `cheshirekow/cmake_format#25`_: cannot invoke cmake-format with python3

.. _cheshirekow/cmake_format#2: https://github.com/cheshirekow/cmake_format/issues/2
.. _cheshirekow/cmake_format#3: https://github.com/cheshirekow/cmake_format/issues/3
.. _cheshirekow/cmake_format#7: https://github.com/cheshirekow/cmake_format/issues/7
.. _cheshirekow/cmake_format#9: https://github.com/cheshirekow/cmake_format/issues/9
.. _cheshirekow/cmake_format#13: https://github.com/cheshirekow/cmake_format/issues/13
.. _cheshirekow/cmake_format#16: https://github.com/cheshirekow/cmake_format/issues/16
.. _cheshirekow/cmake_format#17: https://github.com/cheshirekow/cmake_format/issues/17
.. _cheshirekow/cmake_format#21: https://github.com/cheshirekow/cmake_format/issues/21
.. _cheshirekow/cmake_format#23: https://github.com/cheshirekow/cmake_format/issues/23
.. _cheshirekow/cmake_format#25: https://github.com/cheshirekow/cmake_format/issues/25

v0.3.4
------

* Don't use tempfile.NamedTemporaryFile because it has different (and,
  honestly, buggy behavior) comparied to codecs.open() or io.open()
* Use io.open() instead of codecs.open(). I'm not sure why to prefer one over
  the other but since io.open is more or less required for printing to stdout
  I'll use io.open for everything
* Lexer consumes windows line endings as line endings
* Add inplace invocation test
* Add line ending configuration parameter
* Add configuration parameter command line documentation
* Add documentation to python config file dump output
* Strip trailing whitespace and normalize line endings in bracket comments

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

v0.2.1
------

* fix bug in reflow if text goes to exactly the end of the line
* add python module documentation to sphinx autodoc
* make formatting of COMMANDs a bit more compact
