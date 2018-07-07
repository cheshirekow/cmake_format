============
cmake format
============

``cmake-format`` can format your listfiles nicely so that they don't look
like crap.

------------
Installation
------------

Install from ``pypi`` using ``pip``::

    pip install --user cmake_format

or::

    sudo pip install cmake_format

-----
Usage
-----

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
    for customization. Run with `--dump-config [yaml|cmake|python]`.

    positional arguments:
      infilepaths

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --dump-config [{yaml,json,python}]
                            If specified, print the default configuration to
                            stdout and exit
      -i, --in-place
      -o OUTFILE_PATH, --outfile-path OUTFILE_PATH
                            Where to write the formatted file. Default is stdout.
      --dump {lex,parse,layout}
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            path to configuration file

    Formatter Configuration:
      Override configfile options

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
      --bullet-char BULLET_CHAR
                            What character to use for bulleted lists
      --enum-char ENUM_CHAR
                            What character to use as punctuation after numerals in
                            an enumerated list
      --line-ending {windows,unix,auto}
                            What style line endings to use in the output.
      --command-case {lower,upper,unchanged}
                            Format command names consistently as 'lower' or
                            'upper' case
      --keyword-case {lower,upper,unchanged}
                            Format keywords consistently as 'lower' or 'upper'
                            case
      --always-wrap [ALWAYS_WRAP [ALWAYS_WRAP ...]]
                            A list of command names which should always be wrapped


-------------
Configuration
-------------

``cmake-format`` accepts configuration files in yaml, json, or python format.
An example configuration file is given here. Additional flags and additional
kwargs will help ``cmake-format`` to break up your custom commands in a
pleasant way.

.. code::

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

    # What character to use for bulleted lists
    bullet_char = u'*'

    # What character to use as punctuation after numerals in an enumerated list
    enum_char = u'.'

    # What style line endings to use in the output.
    line_ending = u'unix'

    # Format command names consistently as 'lower' or 'upper' case
    command_case = u'lower'

    # Format keywords consistently as 'lower' or 'upper' case
    keyword_case = u'unchanged'

    # Specify structure for custom cmake functions
    additional_commands = {
      "foo": {
        "flags": [
          "BAR",
          "BAZ"
        ],
        "kwargs": {
          "HEADERS": "*",
          "DEPENDS": "*",
          "SOURCES": "*"
        }
      }
    }

    # A list of command names which should always be wrapped
    always_wrap = []

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
is encountered (the bullet must be at the same indentation level). The list must
be surrounded by a pair of empty lines. Nested lists will be formatted in
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

-------
Issues
-------

If you encounter any bugs or regressions or if ``cmake-format`` doesn't behave
in the way that you expect, please post an issue on the `github issue tracker`_.
It is especially helpful if you can provide cmake listfile snippets that
demonstrate any issues you encounter.

.. _`github issue tracker`: https://github.com/cheshirekow/cmake_format/issues

-------
Example
-------

Will turn this:

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


into this:

.. code:: cmake

    # The following multiple newlines should be collapsed into a single newline

    cmake_minimum_required(VERSION 2.8.11)
    project(cmake_format_test)

    # This multiline-comment should be reflowed into a single comment on one line

    # This comment should remain right before the command call. Furthermore, the
    # command call should be formatted to a single line.
    add_subdirectories(foo bar baz foo2 bar2 baz2)

    # This very long command should be split to multiple lines
    set(HEADERS
        very_long_header_name_a.h
        very_long_header_name_b.h
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
        DEPENDS foo bar baz)

    # This command uses a string with escaped quote chars
    foo(some_arg some_arg "This is a \"string\" within a string")

    # This command uses an empty string
    foo(some_arg some_arg "")

    # This command uses a multiline string
    foo(some_arg some_arg "
        This string is on multiple lines
    ")
