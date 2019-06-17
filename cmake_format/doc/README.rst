============
cmake format
============

.. image:: https://travis-ci.com/cheshirekow/cmake_format.svg?branch=master
    :target: https://travis-ci.com/cheshirekow/cmake_format

.. image:: https://readthedocs.org/projects/cmake-format/badge/?version=latest
    :target: https://cmake-format.readthedocs.io

``cmake-format`` can format your listfiles nicely so that they don't look
like crap.

------------
Installation
------------

Install from ``pypi`` using ``pip``::

    pip install cmake_format

------------
Integrations
------------

* There is an official `vscode extension`__
* Someone also created a `sublime plugin`__

.. __: https://marketplace.visualstudio.com/items?itemName=cheshirekow.cmake-format
.. __: https://packagecontrol.io/packages/CMakeFormat

-----
Usage
-----

.. dynamic: usage-begin

.. code:: text

    usage:
    cmake-format [-h]
                 [--dump-config {yaml,json,python} | -i | -o OUTFILE_PATH]
                 [-c CONFIG_FILE]
                 infilepath [infilepath ...]

    Parse cmake listfiles and format them nicely.

    Formatting is configurable by providing a configuration file. The configuration
    file can be in json, yaml, or python format. If no configuration file is
    specified on the command line, cmake-format will attempt to find a suitable
    configuration for each ``inputpath`` by checking recursively checking it's
    parent directory up to the root of the filesystem. It will return the first
    file it finds with a filename that matches '\.?cmake-format(.yaml|.json|.py)'.

    cmake-format can spit out the default configuration for you as starting point
    for customization. Run with `--dump-config [yaml|json|python]`.

    positional arguments:
      infilepaths

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --dump-config [{yaml,json,python}]
                            If specified, print the default configuration to
                            stdout and exit
      --dump {lex,parse,layout,markup}
      -i, --in-place
      -o OUTFILE_PATH, --outfile-path OUTFILE_PATH
                            Where to write the formatted file. Default is stdout.
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            path to configuration file

    Formatter Configuration:
      Override configfile options affecting general formatting

      --line-width LINE_WIDTH
                            How wide to allow formatted cmake files
      --tab-size TAB_SIZE   How many spaces to tab for indent
      --max-subargs-per-line MAX_SUBARGS_PER_LINE
                            If arglists are longer than this, break them always
      --separate-ctrl-name-with-space [SEPARATE_CTRL_NAME_WITH_SPACE]
                            If true, separate flow control names from their
                            parentheses with a space
      --separate-fn-name-with-space [SEPARATE_FN_NAME_WITH_SPACE]
                            If true, separate function names from parentheses with
                            a space
      --dangle-parens [DANGLE_PARENS]
                            If a statement is wrapped to more than one line, than
                            dangle the closing parenthesis on it's own line
      --max-prefix-chars MAX_PREFIX_CHARS
                            If the statement spelling length (including space and
                            parenthesis is larger than the tab width by more than
                            this amoung, then force reject un-nested layouts.
      --max-lines-hwrap MAX_LINES_HWRAP
                            If a candidate layout is wrapped horizontally but it
                            exceeds this many lines, then reject the layout.
      --line-ending {windows,unix,auto}
                            What style line endings to use in the output.
      --command-case {lower,upper,canonical,unchanged}
                            Format command names consistently as 'lower' or
                            'upper' case
      --keyword-case {lower,upper,unchanged}
                            Format keywords consistently as 'lower' or 'upper'
                            case
      --always-wrap [ALWAYS_WRAP [ALWAYS_WRAP ...]]
                            A list of command names which should always be wrapped
      --algorithm-order [ALGORITHM_ORDER [ALGORITHM_ORDER ...]]
                            Specify the order of wrapping algorithms during
                            successive reflow attempts
      --enable-sort [ENABLE_SORT]
                            If true, the argument lists which are known to be
                            sortable will be sorted lexicographicall
      --autosort [AUTOSORT]
                            If true, the parsers may infer whether or not an
                            argument list is sortable (without annotation).
      --hashruler-min-length HASHRULER_MIN_LENGTH
                            If a comment line starts with at least this many
                            consecutive hash characters, then don't lstrip() them
                            off. This allows for lazy hash rulers where the first
                            hash char is not separated by space

    Comment Formatting:
      Override config options affecting comment formatting

      --bullet-char BULLET_CHAR
                            What character to use for bulleted lists
      --enum-char ENUM_CHAR
                            What character to use as punctuation after numerals in
                            an enumerated list
      --enable-markup [ENABLE_MARKUP]
                            enable comment markup parsing and reflow
      --first-comment-is-literal [FIRST_COMMENT_IS_LITERAL]
                            If comment markup is enabled, don't reflow the first
                            comment block in each listfile. Use this to preserve
                            formatting of your copyright/license statements.
      --literal-comment-pattern LITERAL_COMMENT_PATTERN
                            If comment markup is enabled, don't reflow any comment
                            block which matches this (regex) pattern. Default is
                            `None` (disabled).
      --fence-pattern FENCE_PATTERN
                            Regular expression to match preformat fences in
                            comments default=r'^\s*([`~]{3}[`~]*)(.*)$'
      --ruler-pattern RULER_PATTERN
                            Regular expression to match rulers in comments
                            default=r'^\s*[^\w\s]{3}.*[^\w\s]{3}$'
      --canonicalize-hashrulers [CANONICALIZE_HASHRULERS]
                            If true, then insert a space between the first hash
                            char and remaining hash chars in a hash ruler, and
                            normalize it's length to fill the column

    Misc Options:
      Override miscellaneous config options

      --emit-byteorder-mark [EMIT_BYTEORDER_MARK]
                            If true, emit the unicode byte-order mark (BOM) at the
                            start of the file
      --input-encoding INPUT_ENCODING
                            Specify the encoding of the input file. Defaults to
                            utf-8.
      --output-encoding OUTPUT_ENCODING
                            Specify the encoding of the output file. Defaults to
                            utf-8. Note that cmake only claims to support utf-8 so
                            be careful when using anything else

.. dynamic: usage-end

-------------
Configuration
-------------

``cmake-format`` accepts configuration files in yaml, json, or python format.
An example configuration file is given here. Additional flags and additional
kwargs will help ``cmake-format`` to break up your custom commands in a
pleasant way.

.. dynamic: configuration-begin

.. code:: text


    # --------------------------
    # General Formatting Options
    # --------------------------
    # How wide to allow formatted cmake files
    line_width = 80

    # How many spaces to tab for indent
    tab_size = 2

    # If arglists are longer than this, break them always
    max_subargs_per_line = 3

    # If true, separate flow control names from their parentheses with a space
    separate_ctrl_name_with_space = False

    # If true, separate function names from parentheses with a space
    separate_fn_name_with_space = False

    # If a statement is wrapped to more than one line, than dangle the closing
    # parenthesis on it's own line
    dangle_parens = False

    # If the statement spelling length (including space and parenthesis is larger
    # than the tab width by more than this amoung, then force reject un-nested
    # layouts.
    max_prefix_chars = 2

    # If a candidate layout is wrapped horizontally but it exceeds this many lines,
    # then reject the layout.
    max_lines_hwrap = 2

    # What style line endings to use in the output.
    line_ending = 'unix'

    # Format command names consistently as 'lower' or 'upper' case
    command_case = 'canonical'

    # Format keywords consistently as 'lower' or 'upper' case
    keyword_case = 'unchanged'

    # Specify structure for custom cmake functions
    additional_commands = {
      "pkg_find": {
        "kwargs": {
          "PKG": "*"
        }
      }
    }

    # A list of command names which should always be wrapped
    always_wrap = []

    # Specify the order of wrapping algorithms during successive reflow attempts
    algorithm_order = [0, 1, 2, 3, 4]

    # If true, the argument lists which are known to be sortable will be sorted
    # lexicographicall
    enable_sort = True

    # If true, the parsers may infer whether or not an argument list is sortable
    # (without annotation).
    autosort = False

    # If a comment line starts with at least this many consecutive hash characters,
    # then don't lstrip() them off. This allows for lazy hash rulers where the first
    # hash char is not separated by space
    hashruler_min_length = 10

    # A dictionary containing any per-command configuration overrides. Currently
    # only `command_case` is supported.
    per_command = {}


    # --------------------------
    # Comment Formatting Options
    # --------------------------
    # What character to use for bulleted lists
    bullet_char = '*'

    # What character to use as punctuation after numerals in an enumerated list
    enum_char = '.'

    # enable comment markup parsing and reflow
    enable_markup = True

    # If comment markup is enabled, don't reflow the first comment block in each
    # listfile. Use this to preserve formatting of your copyright/license
    # statements.
    first_comment_is_literal = False

    # If comment markup is enabled, don't reflow any comment block which matches
    # this (regex) pattern. Default is `None` (disabled).
    literal_comment_pattern = None

    # Regular expression to match preformat fences in comments
    # default=r'^\s*([`~]{3}[`~]*)(.*)$'
    fence_pattern = '^\\s*([`~]{3}[`~]*)(.*)$'

    # Regular expression to match rulers in comments
    # default=r'^\s*[^\w\s]{3}.*[^\w\s]{3}$'
    ruler_pattern = '^\\s*[^\\w\\s]{3}.*[^\\w\\s]{3}$'

    # If true, then insert a space between the first hash char and remaining hash
    # chars in a hash ruler, and normalize it's length to fill the column
    canonicalize_hashrulers = True


    # ---------------------------------
    # Miscellaneous Options
    # ---------------------------------
    # If true, emit the unicode byte-order mark (BOM) at the start of the file
    emit_byteorder_mark = False

    # Specify the encoding of the input file. Defaults to utf-8.
    input_encoding = 'utf-8'

    # Specify the encoding of the output file. Defaults to utf-8. Note that cmake
    # only claims to support utf-8 so be careful when using anything else
    output_encoding = 'utf-8'


.. dynamic: configuration-end

You may specify a path to a configuration file with the ``--config-file``
command line option. Otherwise, ``cmake-format`` will search the ancestry
of each ``infilepath`` looking for a configuration file to use. If no
configuration file is found it will use sensible defaults.

A automatically detected configuration files may have any name that matches
``\.?cmake-format(.yaml|.json|.py)``.

If you'd like to create a new configuration file, ``cmake-format`` can help
by dumping out the default configuration in your preferred format. You can run
``cmake-format --dump-config [yaml|json|python]`` to print the default
configuration ``stdout`` and use that as a starting point.

.. dynamic: features-begin

-------
Markup
-------

``cmake-format`` is for the exceptionally lazy. It will even format your
comments for you. It will reflow your comment text to within the configured
line width. It also understands a very limited markup format for a couple of
common bits.

**rulers**: A ruler is a line which starts with and ends with three or more
non-alphanum or space characters::

    # ---- This is a Ruler ----
    # cmake-format will know to keep the ruler separated from the
    # paragraphs around it. So it wont try to reflow this text as
    # a single paragraph.
    # ---- This is also a Ruler ---


**list**: A list is started on the first encountered list item, which starts
with a bullet character (``*``) followed by a space followed by some text.
Subsequent lines will be included in the list item until the next list item
is encountered (the bullet must be at the same indentation level). The list
must be surrounded by a pair of empty lines. Nested lists will be formatted in
nested text::

    # here are some lists:
    #
    # * item 1
    # * item 2
    #
    #   * subitem 1
    #   * subitem 2
    #
    # * second list item 1
    # * second list item 2

**enumerations**: An enumeration is similar to a list but the bullet character
is some integers followed by a period. New enumeration items are detected as
long as either the first digit or the punctuation lines up in the same column
as the previous item. ``cmake-format`` will renumber your items and align their
labels for you::

    # This is an enumeration
    #
    #   1. item
    #   2. item
    #   3. item

**fences**: If you have any text which you do not want to be formatted you can
guard it with a pair of fences. Fences are three or more tilde characters::

    # ~~~
    # This comment is fenced
    #   and will not be formatted
    # ~~~

Note that comment fences guard reflow of *comment text*, and not cmake code.
If you wish to prevent formatting of cmake, code, see below. In addition to
fenced-literals, there are three other ways to preserve comment text from
markup and/or reflow processing:

* The ``--first-comment-is-literal`` configuration option will exactly preserve
  the first comment in the file. This is intended to preserve copyright or
  other formatted header comments.
* The ``--literal-comment-pattern`` configuration option allows for a more
  generic way to identify comments which should be preserved literally. This
  configuration takes a regular expression pattern.
* The ``--enable-markup`` configuration option globally enables comment markup
  processing. It defaults to true so set it to false if you wish to globally
  disable comment markup processing. Note that trailing whitespace is still
  chomped from comments.

--------------------------
Disable Formatting Locally
--------------------------

You can locally disable and enable code formatting by using the special
comments ``# cmake-format: off`` and ``# cmake-format: on``.

-------------------
Sort Argument Lists
-------------------

Starting with version `0.5.0`, ``cmake-format`` can sort your argument lists
for you. If the configuration includes ``autosort=True`` (the default), it
will replace::

    add_library(foobar STATIC EXCLUDE_FROM_ALL
                sourcefile_06.cc
                sourcefile_03.cc
                sourcefile_02.cc
                sourcefile_04.cc
                sourcefile_07.cc
                sourcefile_01.cc
                sourcefile_05.cc)

with::

    add_library(foobar STATIC EXCLUDE_FROM_ALL
                sourcefile_01.cc
                sourcefile_02.cc
                sourcefile_03.cc
                sourcefile_04.cc
                sourcefile_05.cc
                sourcefile_06.cc
                sourcefile_07.cc)

This is implemented for any argument lists which the parser knows are
inherently sortable. This includes the following cmake commands:

* ``add_library``
* ``add_executable``

For most other cmake commands, you can use an annotation comment to hint to
``cmake-format`` that the argument list is sortable. For instance::

    set(SOURCES
        # cmake-format: sortable
        bar.cc
        baz.cc
        foo.cc)

Annotations can be given in a line-comment or a bracket comment. There is a
long-form and a short-form for each. The acceptable formats are:

+-----------------+-------+------------------------------+
| Line Comment    | long  | ``# cmake-format: <tag>``    |
+-----------------+-------+------------------------------+
| Line Comment    | short | ``# cmf: <tag>``             |
+-----------------+-------+------------------------------+
| Bracket Comment | long  | ``#[[cmake-format: <tag>]]`` |
+-----------------+-------+------------------------------+
| Bracket Comment | short | ``#[[cmf: <tag>]]``          |
+-----------------+-------+------------------------------+

In order to annotate a positional argument list as sortable, the acceptable
tags are: ``sortable`` or ``sort``. For the commands listed above where
the positinal argument lists are inherently sortable, you can locally disable
sorting by annotating them with ``unsortable`` or ``unsort``. For example::

    add_library(foobar STATIC
                # cmake-format: unsort
                sourcefile_03.cc
                sourcefile_01.cc
                sourcefile_02.cc)

Note that this is only needed if your configuration has enabled ``autosort``,
and you can globally disable sorting by making setting this configuration to
``False``.

.. dynamic: features-end

---------------------------------
Reporting Issues and Getting Help
---------------------------------

If you encounter any bugs or regressions or if ``cmake-format`` doesn't behave
in the way that you expect, please post an issue on the
`github issue tracker`_. It is especially helpful if you can provide cmake
listfile snippets that demonstrate any issues you encounter.

.. _`github issue tracker`: https://github.com/cheshirekow/cmake_format/issues

You can also join the ``#cmake-format`` channel on our discord server.

.. _`discord server`: https://discord.gg/NgjwyPy


----------
Developers
----------

Some notes for anyone who wants hack on ``cmake-format``:

1. Please use ``pylint`` to check your code. There is a pylint config file in
   the repo.
2. There is a test suite in ``tests.py``. Run with
   ``python -Bm cmake_format.tests`` (ensure modified code is on the python
   path).
3. There's an ``autopep8`` config file in the repo as well. Feel free to use
   that to format the code. Note that ``autopep8`` and ``pylint`` disagree
   in a few places so using ``autopep8`` may require some manual edits
   afterward.
4. There's a cmake configuration for the project. Since this is a python
   project there isn't much that it really does but it provides targets for
   ``format``, ``lint`` and ``test`` if you'd like to use them.

-------
Example
-------

Will turn this:

.. dynamic: example-in-begin

.. code:: cmake

    # The following multiple newlines should be collapsed into a single newline




    cmake_minimum_required(VERSION 2.8.11)
    project(cmake_format_test)

    # This multiline-comment should be reflowed
    # into a single comment
    # on one line

    # This comment should remain right before the command call.
    # Furthermore, the command call should be formatted
    # to a single line.
    add_subdirectories(foo bar baz
      foo2 bar2 baz2)

    # This very long command should be split to multiple lines
    set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)

    # This command should be split into one line per entry because it has a long
    # argument list.
    set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc source_g.cc)

    # The string in this command should not be split
    set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")

    # This command has a very long argument and can't be aligned with the command
    # end, so it should be moved to a new line with block indent + 1.
    some_long_command_name("Some very long argument that really needs to be on the next line.")

    # This situation is similar but the argument to a KWARG needs to be on a
    # newline instead.
    set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")

    set(HEADERS header_a.h header_b.h # This comment should
                                      # be preserved, moreover it should be split
                                      # across two lines.
        header_c.h header_d.h)


    # This part of the comment should
    # be formatted
    # but...
    # cmake-format: off
    # This bunny should remain untouched:
    # . 　 ＿　∩
    # 　　ﾚﾍヽ| |
    # 　　　 (・ｘ・)
    # 　　 c( uu}
    # cmake-format: on
    #          while this part should
    #          be formatted again

    # This is a paragraph
    #
    # This is a second paragraph
    #
    # This is a third paragraph

    # This is a comment
    # that should be joined but
    # TODO(josh): This todo should not be joined with the previous line.
    # NOTE(josh): Also this should not be joined with the todo.

    if(foo)
    if(sbar)
    # This comment is in-scope.
    add_library(foo_bar_baz foo.cc bar.cc # this is a comment for arg2
                   # this is more comment for arg2, it should be joined with the first.
        baz.cc) # This comment is part of add_library

    other_command(some_long_argument some_long_argument) # this comment is very long and gets split across some lines

    other_command(some_long_argument some_long_argument some_long_argument) # this comment is even longer and wouldn't make sense to pack at the end of the command so it gets it's own lines
    endif()
    endif()


    # This very long command should be broken up along keyword arguments
    foo(nonkwarg_a nonkwarg_b HEADERS a.h b.h c.h d.h e.h f.h SOURCES a.cc b.cc d.cc DEPENDS foo bar baz)

    # This command uses a string with escaped quote chars
    foo(some_arg some_arg "This is a \"string\" within a string")

    # This command uses an empty string
    foo(some_arg some_arg "")

    # This command uses a multiline string
    foo(some_arg some_arg "
        This string is on multiple lines
    ")

    # No, I really want this to look ugly
    # cmake-format: off
    add_library(a b.cc
      c.cc         d.cc
               e.cc)
    # cmake-format: on

.. dynamic: example-in-end

into this:

.. dynamic: example-out-begin

.. code:: cmake

    # The following multiple newlines should be collapsed into a single newline

    cmake_minimum_required(VERSION 2.8.11)
    project(cmake_format_test)

    # This multiline-comment should be reflowed into a single comment on one line

    # This comment should remain right before the command call. Furthermore, the
    # command call should be formatted to a single line.
    add_subdirectories(foo
                       bar
                       baz
                       foo2
                       bar2
                       baz2)

    # This very long command should be split to multiple lines
    set(HEADERS very_long_header_name_a.h very_long_header_name_b.h
                very_long_header_name_c.h)

    # This command should be split into one line per entry because it has a long
    # argument list.
    set(SOURCES
        source_a.cc
        source_b.cc
        source_d.cc
        source_e.cc
        source_f.cc
        source_g.cc)

    # The string in this command should not be split
    set_target_properties(foo bar baz
                          PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")

    # This command has a very long argument and can't be aligned with the command
    # end, so it should be moved to a new line with block indent + 1.
    some_long_command_name(
      "Some very long argument that really needs to be on the next line.")

    # This situation is similar but the argument to a KWARG needs to be on a newline
    # instead.
    set(CMAKE_CXX_FLAGS
        "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")

    set(HEADERS
        header_a.h
        header_b.h # This comment should be preserved, moreover it should be split
                   # across two lines.
        header_c.h
        header_d.h)

    # This part of the comment should be formatted but...
    # cmake-format: off
    # This bunny should remain untouched:
    # . 　 ＿　∩
    # 　　ﾚﾍヽ| |
    # 　　　 (・ｘ・)
    # 　　 c( uu}
    # cmake-format: on
    # while this part should be formatted again

    # This is a paragraph
    #
    # This is a second paragraph
    #
    # This is a third paragraph

    # This is a comment that should be joined but
    # TODO(josh): This todo should not be joined with the previous line.
    # NOTE(josh): Also this should not be joined with the todo.

    if(foo)
      if(sbar)
        # This comment is in-scope.
        add_library(foo_bar_baz
                    foo.cc
                    bar.cc # this is a comment for arg2 this is more comment for
                           # arg2, it should be joined with the first.
                    baz.cc) # This comment is part of add_library

        other_command(some_long_argument some_long_argument) # this comment is very
                                                             # long and gets split
                                                             # across some lines

        other_command(some_long_argument some_long_argument some_long_argument)
        # this comment is even longer and wouldn't make sense to pack at the end of
        # the command so it gets it's own lines
      endif()
    endif()

    # This very long command should be broken up along keyword arguments
    foo(nonkwarg_a nonkwarg_b
        HEADERS a.h
                b.h
                c.h
                d.h
                e.h
                f.h
        SOURCES a.cc b.cc d.cc
        DEPENDS foo
        bar baz)

    # This command uses a string with escaped quote chars
    foo(some_arg some_arg "This is a \"string\" within a string")

    # This command uses an empty string
    foo(some_arg some_arg "")

    # This command uses a multiline string
    foo(some_arg some_arg "
        This string is on multiple lines
    ")

    # No, I really want this to look ugly
    # cmake-format: off
    add_library(a b.cc
      c.cc         d.cc
               e.cc)
    # cmake-format: on

.. dynamic: example-out-end
