=======================
Configuration and Usage
=======================

-------------
Configuration
-------------

``cmake-format`` accepts configuration files in yaml, json, or python format.

.. note::

  ``cmake-format`` requires the ``pyyaml`` python package in order to
  consume yaml as the configuration file. This dependency is not enforced
  by default during installation since this is an optional feature. It can
  be enabled by installing with a command like
  ``pip install cmake_format[YAML]``

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

    # If an argument group contains more than this many sub-groups (parg or kwarg
    # groups), then force it to a vertical layout.
    max_subgroups_hwrap = 2

    # If a positinal argument group contains more than this many arguments, then
    # force it to a vertical layout.
    max_pargs_hwrap = 6

    # If true, separate flow control names from their parentheses with a space
    separate_ctrl_name_with_space = False

    # If true, separate function names from parentheses with a space
    separate_fn_name_with_space = False

    # If a statement is wrapped to more than one line, than dangle the closing
    # parenthesis on it's own line.
    dangle_parens = False

    # If the trailing parenthesis must be 'dangled' on it's on line, then align it
    # to this reference: `prefix`: the start of the statement,  `prefix-indent`: the
    # start of the statement, plus one indentation  level, `child`: align to the
    # column of the arguments
    dangle_align = 'prefix'

    min_prefix_chars = 4

    # If the statement spelling length (including space and parenthesis is larger
    # than the tab width by more than this amoung, then force reject un-nested
    # layouts.
    max_prefix_chars = 10

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

    # A dictionary mapping layout nodes to a list of wrap decisions. See the
    # documentation for more information.
    layout_passes = {}


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
      -l {error,warning,info,debug}, --log-level {error,warning,info,debug}
      --dump-config [{yaml,json,python}]
                            If specified, print the default configuration to
                            stdout and exit
      --dump {lex,parse,layout,markup}
      -i, --in-place
      -o OUTFILE_PATH, --outfile-path OUTFILE_PATH
                            Where to write the formatted file. Default is stdout.
      -c CONFIG_FILES [CONFIG_FILES ...], --config-files CONFIG_FILES [CONFIG_FILES ...]
                            path to configuration file(s)

    Formatter Configuration:
      Override configfile options affecting general formatting

      --line-width LINE_WIDTH
                            How wide to allow formatted cmake files
      --tab-size TAB_SIZE   How many spaces to tab for indent
      --max-subgroups-hwrap MAX_SUBGROUPS_HWRAP
                            If an argument group contains more than this many sub-
                            groups (parg or kwarg groups), then force it to a
                            vertical layout.
      --max-pargs-hwrap MAX_PARGS_HWRAP
                            If a positinal argument group contains more than this
                            many arguments, then force it to a vertical layout.
      --separate-ctrl-name-with-space [SEPARATE_CTRL_NAME_WITH_SPACE]
                            If true, separate flow control names from their
                            parentheses with a space
      --separate-fn-name-with-space [SEPARATE_FN_NAME_WITH_SPACE]
                            If true, separate function names from parentheses with
                            a space
      --dangle-parens [DANGLE_PARENS]
                            If a statement is wrapped to more than one line, than
                            dangle the closing parenthesis on it's own line.
      --dangle-align {prefix,prefix-indent,child,off}
                            If the trailing parenthesis must be 'dangled' on it's
                            on line, then align it to this reference: `prefix`:
                            the start of the statement, `prefix-indent`: the start
                            of the statement, plus one indentation level, `child`:
                            align to the column of the arguments
      --min-prefix-chars MIN_PREFIX_CHARS
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
