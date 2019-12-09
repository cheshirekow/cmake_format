=========
Changelog
=========

-----------
v0.6 series
-----------

v0.6.3
------

* Add ``ctest-to`` program
* Add ``cmake-lint`` program
* Separate documentation by program
* Add some more detailed configuration documentation
* Make some of the config logic generic and push into a base class
* Some groundwork for cleaning up the config into different sections
* Fix externalproject_add_stepdependencies


* Closes `#152`_: AssertionError on externalproject_add_stepdependencies

.. _#152: https://github.com/cheshirekow/cmake_format/issues/152

v0.6.2
------

* some initial work on cmake helptext/usage parser
* fix set_target_properties
* fix TOUCH_NOCREATE
* copymode during --in-place
* add --check command
* supress spurious warnings in tests
* create add_custom_target parser
* update add_custom_command parser with different forms
* fix target form of install command
* implement require-valid-layout and add tests
* sidecar tests don't need a companion pyfile
* fix some typos in documentation


* Closes `#133`_: Better handling of un-wrappable, too-long lines
* Closes `#134`_: Wrong formatting of install(TARGETS)
* Closes `#140`_: add USES_TERMINAL to kwargs
* Closes `#142`_: Add a --check option that doesn't write the files
* Closes `#143`_: Broken file attributes after formatting
* Closes `#144`_: Wrong warning about "file(TOUCH_NOCREATE ...)"
* Closes `#145`_: Bad formatting for `set_target_properties`
* Closes `#147`_: foreach format
* Closes `#150`_: Contributing documentation
* Closes `#151`_: README.rst: fix two typos


.. _#133: https://github.com/cheshirekow/cmake_format/issues/133
.. _#134: https://github.com/cheshirekow/cmake_format/issues/134
.. _#140: https://github.com/cheshirekow/cmake_format/issues/140
.. _#142: https://github.com/cheshirekow/cmake_format/issues/142
.. _#143: https://github.com/cheshirekow/cmake_format/issues/143
.. _#144: https://github.com/cheshirekow/cmake_format/issues/144
.. _#145: https://github.com/cheshirekow/cmake_format/issues/145
.. _#147: https://github.com/cheshirekow/cmake_format/issues/147
.. _#150: https://github.com/cheshirekow/cmake_format/issues/150
.. _#151: https://github.com/cheshirekow/cmake_format/issues/151


v0.6.1
------

* consolidate ``--config-file`` command line flag variants
* add documentation on integration with ``pre-commit``
* add documentation on sidecar tests
* simplify the tag format for sidecar tests
* add support of config options and lex/parse/layout assertions in sidecar
  tests
* add documentation on debugging with tests
* add tests to validate pull requests
* move most tests into sidecar files


v0.6.0
------

Significant refactor of the formatting logic.

* Move ``format_tests`` into ``command_tests.misc_tests``
* Prototype sidecar tests for easier readability/maintainability
* ArgGroupNodes gain representation in the layout tree
* Get rid of ``WrapAlgo``
* Eliminate vertical/nest as separate decisions. Nesting is just the wrap
  decision for StatementNode and KwargNode wheras vertical is the wrap
  decision for PargGroupnode and ArgGroupNode.
* Replace ``algorithm_order`` with ``_layout_passes``
* Get rid of ``default_accept_layout`` and move logic into a member function
* Move configuration and ``node_path`` into new ``StackContext``
* Stricter valid-child-set for most layout nodes

-----------
v0.5 series
-----------

v0.5.5
------

* Python config files now have ``__file__`` set in the global namespace
* Add parse support for ``BYPRODUCTS`` in ``add_custom_command``
* Modify vscode extension cwd  to better support subtree configuration files
* Fix vscode extension args type configuration
* Support multiple config files


* Closes `#121`_: Support ``BYPRODUCTS``
* Closes `#123`_: Allow multiple config files
* Closes `#125`_: Swap ordering of cwd location in vscode extension
* Closes `#128`_: Include LICENSE.txt in sdist and wheel
* Closes `#129`_: cmakeFormat.args in settings.json yields Incorrect type
* Closes `#131`_: cmakeFormat.args is an array of items of type string

.. _#121: https://github.com/cheshirekow/cmake_format/issues/121
.. _#123: https://github.com/cheshirekow/cmake_format/issues/123
.. _#125: https://github.com/cheshirekow/cmake_format/issues/125
.. _#128: https://github.com/cheshirekow/cmake_format/issues/128
.. _#129: https://github.com/cheshirekow/cmake_format/issues/129
.. _#131: https://github.com/cheshirekow/cmake_format/issues/131


v0.5.4
------

* Don't write un-changed file content when doing in-place formatting
* Fix windows line-endings dropped during read
* Add documentation on how to add custom commands
* Fix yaml-loader returns None instead of empty dictionary for an empty yaml
  config file.


* Closes `#114`_: Example of adding custom cmake functions/macros
* Closes `#117`_: Fix handling of --dump-config with empty existing yaml config
* Closes `#118`_: Avoid writing outfile unnecessarily
* Closes `#119`_: Fix missing newline argument
* Closes `#120`_: auto-line ending option not working correctly under Windows

.. _#114: https://github.com/cheshirekow/cmake_format/issues/114
.. _#117: https://github.com/cheshirekow/cmake_format/issues/117
.. _#118: https://github.com/cheshirekow/cmake_format/issues/118
.. _#119: https://github.com/cheshirekow/cmake_format/issues/119
.. _#120: https://github.com/cheshirekow/cmake_format/issues/120

v0.5.3
------

* add some configuration options for next format Refactor
* update documentation source generator scripts and run to get updated
  dynamic doc texts
* add a couple more case studies
* split reflow methods into smaller methods per case
* fix os.expanduser on None


* Closes `#115`_: crash when no config file

.. _#115: https://github.com/cheshirekow/cmake_format/issues/115


v0.5.2
------

* add parsers for different forms of ``add_library()`` and ``add_executable()``
* move ``add_library``, ``add_executable()`` and ``install()`` parsers to their
  own modules
* don't infer sortability in ``add_library`` or ``add_executable()`` if the
  descriminator token might be a cmake variable hiding the descriminator
  spelling
* Split configuration options into different groups during dump and --help
* Refactor long ``_reflow()`` implementations, splitting into methods for
  the different wrap cases. This is in preparation for the next rev of the
  format algorithm.
* Add documentation on the format algorithm and some case studies.
* Autosort defaults to ``False``
* Changed documentation theme to something based on rtd
* Get rid of ``COMMAND`` kwarg specialization


* Closes `#111`_: Formatting breaks ``add_library``
* Closes `#112`_: expanduser on configfile_path

.. _#111: https://github.com/cheshirekow/cmake_format/issues/111
.. _#112: https://github.com/cheshirekow/cmake_format/issues/112

v0.5.1
------

* Fix empty kwarg can yield a parg group node with only whitespace
  children
* Fix ``file(READ ...)`` and ``file(STRINGS ...)`` parser kwargs using set
  syntax instead of dict syntax
* Fix agressive positional parser within conditional parser
* Fix missing endif, endwhile in parsemap
* Split parse functions out into separate modules for better organization
* Add more sanity tests for ``file(...)``.
* Remove README from online docs, replace with expanded documentation for
  each README section
* Restore ability to accept paren-group in arbitrary parg-group
* Fix missing tests on travis
* Fix new tests using unicode literals (affects python2)
* Fix command parser after --


* Closes `#104`_: Extra space for export targets
* Closes `#106`_: Formatting of ``file(READ)`` fails
* Closes `#107`_: multiline cmake commands
* Closes `#108`_: Formatting of ``file(STRING)`` fails
* Closes `#110`_: Formatting of Nested Expressions Fails

.. _#104: https://github.com/cheshirekow/cmake_format/issues/104
.. _#106: https://github.com/cheshirekow/cmake_format/issues/106
.. _#107: https://github.com/cheshirekow/cmake_format/issues/107
.. _#108: https://github.com/cheshirekow/cmake_format/issues/108
.. _#110: https://github.com/cheshirekow/cmake_format/issues/110

v0.5.0
------

* Implement canonical command case
* Canonicalize capitalization of keys in cmdspec
* Add README documentation regarding fences and enable/disable
* Statement parsers are now generic functions. Old standard parser remains
  for most statements, but some statements now have custom parsers.
* Implement deeper parse logic for ``install()`` and ``file()`` commands,
  improving the formatting of these statements.
* Implement input/output encoding configuration parameters
* Implement hashruler markup logic and preserve hashrulers if markup is
  disable or if configured to do so.
* Implement autosort and sortable tagging
* Separate cmake-annotate frontend
* Provider a ``Loader=`` to yaml ``load()``
* Fix python3 lint
* Fix bad lexing of make-style variables
* Fix multiple hash chars ``lstrip()ed`` from comments


* Closes `#62`_: Possible improvement on formatting "file"
* Closes `#75`_: configurable positioning of flags
* Closes `#87`_: Hash-rulers are stripped when markup disabled
* Closes `#91`_: Add missing keyword arguments to project command
* Closes `#95`_: added argument --encoding to allow for non-utf8
* Closes `#98`_: Fix kwargs/flag index for non-lowercase functions
* Closes `#100`_: Extra linebreak inserted when '$(' encountered
* Closes `#101`_: Provide a Loader to yaml.load
* Closes `#102`_: fences does not work as expected

.. _#62: https://github.com/cheshirekow/cmake_format/issues/62
.. _#75: https://github.com/cheshirekow/cmake_format/issues/75
.. _#87: https://github.com/cheshirekow/cmake_format/issues/87
.. _#91: https://github.com/cheshirekow/cmake_format/issues/91
.. _#95: https://github.com/cheshirekow/cmake_format/issues/95
.. _#98: https://github.com/cheshirekow/cmake_format/issues/98
.. _#100: https://github.com/cheshirekow/cmake_format/issues/100
.. _#101: https://github.com/cheshirekow/cmake_format/issues/101
.. _#102: https://github.com/cheshirekow/cmake_format/issues/102

-----------
v0.4 series
-----------

v0.4.5
------

* Fix testing instructions in README
* Fix dump-config instructions in README
* Remove numpy dependency
* Add travis CI configuration
* Fix some issues with lint under python3


* Closes `#40`_
* Closes `#76`_
* Closes `#77`_
* Closes `#80`_
* Fixes `#82`_: Keyword + long coment + long argument asserts

.. _#40: https://github.com/cheshirekow/cmake_format/issues/40
.. _#76: https://github.com/cheshirekow/cmake_format/issues/76
.. _#77: https://github.com/cheshirekow/cmake_format/issues/77
.. _#80: https://github.com/cheshirekow/cmake_format/issues/80
.. _#82: https://github.com/cheshirekow/cmake_format/issues/82

v0.4.4
------

* Fix bug where rulers wouldn't break bulleted lists in comment markup
* Add missing flags COMPONENT and CONFIGURATIONS to command spec
* add ``--dump markup`` to dump the markup parse tree for debugging comment
  formatting behavior
* fix `invalid NoneType value` for `--literal-comment-pattern`
* shebang is preserved if present (without additional options)
* fix trailing comment of kwarg group consumes rparen
* add test to verify correct consumption of args matching outer kwargs
* add new quoted assignment pattern to lexer for cases like quoted compile
  definitions
* add `--dump html-stub` and `--dump html-page` listfile renderers


* Fixes `#56`_: ignores boolean configuration values
* Closes `#66`_: Positional argument of keyword incorrectly matched as keyword
  of containing command
* Resolves `#73`_: Control of macro/function renaming
* Fixes `#74`_: shebang in cmake scripts
* Fixes `#79`_: BOM (Byte-order-mark) crashes parser
* Closes `#81`_: Fix comment handling in kwarg group
* Fixes `#85`_: commands: find_package broken
* Fixes `#86`_: Breaking in Quotes


.. _#56: https://github.com/cheshirekow/cmake_format/issues/56
.. _#66: https://github.com/cheshirekow/cmake_format/issues/66
.. _#73: https://github.com/cheshirekow/cmake_format/issues/73
.. _#74: https://github.com/cheshirekow/cmake_format/issues/74
.. _#79: https://github.com/cheshirekow/cmake_format/issues/79
.. _#81: https://github.com/cheshirekow/cmake_format/issues/81
.. _#85: https://github.com/cheshirekow/cmake_format/issues/85
.. _#86: https://github.com/cheshirekow/cmake_format/issues/86

v0.4.3
------

* dump_config now dumps the active config, including loaded from file or
  modified by command line
* use cmake macros for cleaner listfiles
* fix argparse defaults override config file settings for boolean args

Closed issues:


* Fixes `#70`_: ignores boolean configuration values

.. _#70: https://github.com/cheshirekow/cmake_format/issues/70

v0.4.2
------

* Add visual studio code extension
* Add algorithm order config option
* Add user specified fence regex config option
* Add user specified ruler regex config option
* Add config option to disable comment formatting altogether
* Fix get_config bug in ``__main__``
* Fix missing elseif command specification
* Fix missing elseif/else paren spacing when specified
* Add enable_markup config option
* Fix kwargstack early breaking in conditionals
* Add some notes for developers.
* Add warning if formatter is inactive at the end of a print
* Add config options to preserve first comment or any matching a regex

Closed issues:


* Fixes `#34`_: if conditions with many elements
* Closes `#35`_: break_before_args
* Implements `#42`_: user specified string for fencing
* Implements `#43`_: allow custom string for rulers
* Fixes `#45`_: config file not loaded properly
* Fixes `#51`_: competing herustics for 2+ argument statements
* Implements `#60`_: option to not reflow initial comment block
* Implements `#61`_: add non-builtin commands
* Fixes `#63`_: elseif like if
* Implements `#65`_: warn if off doesn't have corresponding on
* Closes `#67`_: global option to not format comments
* Fixes `#68`_: seperate-ctrl-name-with-space

.. _#34: https://github.com/cheshirekow/cmake_format/issues/34
.. _#35: https://github.com/cheshirekow/cmake_format/issues/35
.. _#42: https://github.com/cheshirekow/cmake_format/issues/42
.. _#43: https://github.com/cheshirekow/cmake_format/issues/43
.. _#45: https://github.com/cheshirekow/cmake_format/issues/45
.. _#51: https://github.com/cheshirekow/cmake_format/issues/51
.. _#60: https://github.com/cheshirekow/cmake_format/issues/60
.. _#61: https://github.com/cheshirekow/cmake_format/issues/61
.. _#63: https://github.com/cheshirekow/cmake_format/issues/63
.. _#65: https://github.com/cheshirekow/cmake_format/issues/65
.. _#67: https://github.com/cheshirekow/cmake_format/issues/67
.. _#68: https://github.com/cheshirekow/cmake_format/issues/68

v0.4.1
------

* Add missing numpy dependency to setup.py
* Fix arg comments dont force vpack
* Fix arg comments dont force dangle parenthesis
* Add some missing function specifications

Closed issues:


* Fixes `#53`_: add numpy as required
* Closes `#54`_: more cmake commands
* Fixes `#55`_: function with interior comment
* Fixes `#56`_: function with trailing comment
* Fixes `#59`_: improve export

.. _#53: https://github.com/cheshirekow/cmake_format/issues/53
.. _#54: https://github.com/cheshirekow/cmake_format/issues/54
.. _#55: https://github.com/cheshirekow/cmake_format/issues/55
.. _#56: https://github.com/cheshirekow/cmake_format/issues/56
.. _#59: https://github.com/cheshirekow/cmake_format/issues/59

v0.4.0
------

* Overhaul parser into a cleaner single-pass implementation that generates a
  more complete representation of the syntax tree.
* Parser now recognizes arbitrary nested command specifications. Keyword
  argument groups are formatted like statements.
* Complete rewrite of formatter (see docs for design)
* Support line comments inside statements and argument groups
* Add some additional command specifications
* Add ``--dump [lex|parse|layout]`` debug commands
* ``--dump-config`` dumps the active configuration (after loading)
* Add keyword case correction
* Improve layout of complicated boolean expressions

Closed issues:


* Implements `#10`_: treat COMPONENT keyword different
* Implements `#37`_: --dump-config dumps current config
* Implements `#39`_: always wrap for certain functions
* Fixes `#46`_: leading comment in function body
* Fixes `#47`_: function argument incorrectly appended
* Implements `#48`_: improve install ``target_*``
* Fixes `#49`_: removes entire while() sections
* Fixes `#50`_: indented comments appended to preceding line

.. _#10: https://github.com/cheshirekow/cmake_format/issues/10
.. _#34: https://github.com/cheshirekow/cmake_format/issues/34
.. _#37: https://github.com/cheshirekow/cmake_format/issues/37
.. _#39: https://github.com/cheshirekow/cmake_format/issues/39
.. _#46: https://github.com/cheshirekow/cmake_format/issues/46
.. _#47: https://github.com/cheshirekow/cmake_format/issues/47
.. _#48: https://github.com/cheshirekow/cmake_format/issues/48
.. _#49: https://github.com/cheshirekow/cmake_format/issues/49
.. _#50: https://github.com/cheshirekow/cmake_format/issues/50

-----------
v0.3 series
-----------

v0.3.6
------

* Implement "auto" line ending option `#27`
* Implement command casing `#29`
* Implement stdin as an input file `#30`

Closed issues:

.. _#27: https://github.com/cheshirekow/cmake_format/issues/27
.. _#29: https://github.com/cheshirekow/cmake_format/issues/29
.. _#30: https://github.com/cheshirekow/cmake_format/issues/30


v0.3.5
------

* Fix `#28`_: lexing pattern for quoted strings with
  escaped quotes
* Add lex tests for quoted strings with escaped quotes
* Fix windows format test

Closed issues:

.. _#28: https://github.com/cheshirekow/cmake_format/issues/28

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

v0.3.3
------

* Convert all string literals in format.py to unicode literals
* Added python3 tests
* Attempt to deal with python2/python3 string differences by using codecs
  and io modules where appropriate. I probably got this wrong somewhere.
* Fix missing comma in config file matching

Closed issues:

* Implement `#13`_: option to dangle parenthesis
* Fix `#17`_: trailing comment stripped from commands
  with no arguments
* Fix `#21`_: corruption upon trailing whitespace
* Fix `#23`_: wrapping long arguments has some weird
  extra newline or missing indentation space.
* Fix `#25`_: cannot invoke cmake-format with python3

.. _#13: https://github.com/cheshirekow/cmake_format/issues/13
.. _#16: https://github.com/cheshirekow/cmake_format/issues/16
.. _#17: https://github.com/cheshirekow/cmake_format/issues/17
.. _#21: https://github.com/cheshirekow/cmake_format/issues/21
.. _#23: https://github.com/cheshirekow/cmake_format/issues/23
.. _#25: https://github.com/cheshirekow/cmake_format/issues/25

v0.3.2
------

* Move configuration to it's own module
* Add lexer/parser support for bracket arguments and bracket comments
* Make stable_wrap work for any ``prefix`` / ``subsequent_prefix``.
* Preserve scope-level bracket comments verbatim
* Add markup module with parse/format support for rudimentary markup in
  comments including nested bulleted and enumerated lists, and fenced blocks.
* Add pyyaml as an extra dependency in pip configuration

Closed issues:

* Fix `#16`_: argparse defaults always override config

v0.3.1
------

* use exec instead of execfile for python3 compatibility

v0.3.0
------

* fix `#2`_ : parser matching builtin logical expression
  names should not be case sensitive
* fix `#3`_ : default code used to read
  ``long_description`` can't decode utf8
* implement `#7`_ : add configuration option to separate
  control statement or function name from parenthesis
* implement `#9`_ : allow configuration options specified
  from command line
* Add support for python as the configfile format
* Add ``--dump-config`` option
* Add support for "separator" lines in comments. Any line consisting of only
  five or more non-alphanum characters will be preserved verbatim.
* Improve python3 support by using ``print_function``

Closed issues:

.. _#2: https://github.com/cheshirekow/cmake_format/issues/2
.. _#3: https://github.com/cheshirekow/cmake_format/issues/3
.. _#7: https://github.com/cheshirekow/cmake_format/issues/7
.. _#9: https://github.com/cheshirekow/cmake_format/issues/9

-----------
v0.2 series
-----------

v0.2.1
------

* fix bug in reflow if text goes to exactly the end of the line
* add python module documentation to sphinx autodoc
* make formatting of COMMANDs a bit more compact

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
