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

.. tag: configuration-begin

.. code:: text

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
    bullet_char = '*'

    # What character to use as punctuation after numerals in an enumerated list
    enum_char = '.'

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
    autosort = True

    # enable comment markup parsing and reflow
    enable_markup = True

    # If comment markup is enabled, don't reflow the first comment block in
    # eachlistfile. Use this to preserve formatting of your
    # copyright/licensestatements.
    first_comment_is_literal = False

    # If comment markup is enabled, don't reflow any comment block which matchesthis
    # (regex) pattern. Default is `None` (disabled).
    literal_comment_pattern = None

    # Regular expression to match preformat fences in comments
    # default=r'^\s*([`~]{3}[`~]*)(.*)$'
    fence_pattern = '^\\s*([`~]{3}[`~]*)(.*)$'

    # Regular expression to match rulers in comments
    # default=r'^\s*[^\w\s]{3}.*[^\w\s]{3}$'
    ruler_pattern = '^\\s*[^\\w\\s]{3}.*[^\\w\\s]{3}$'

    # If true, emit the unicode byte-order mark (BOM) at the start of the file
    emit_byteorder_mark = False

    # If a comment line starts with at least this many consecutive hash characters,
    # then don't lstrip() them off. This allows for lazy hash rulers where the first
    # hash char is not separated by space
    hashruler_min_length = 10

    # If true, then insert a space between the first hash char and remaining hash
    # chars in a hash ruler, and normalize it's length to fill the column
    canonicalize_hashrulers = True

    # Specify the encoding of the input file. Defaults to utf-8.
    input_encoding = 'utf-8'

    # Specify the encoding of the output file. Defaults to utf-8. Note that cmake
    # only claims to support utf-8 so be careful when using anything else
    output_encoding = 'utf-8'

    # A dictionary containing any per-command configuration overrides. Currently
    # only `command_case` is supported.
    per_command = {}


.. tag: configuration-end

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


.. tag: usage-begin

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
      --autosort [AUTOSORT]
                            If true, the argument lists which are known to be
                            sortable will be sorted lexicographicall
      --enable-markup [ENABLE_MARKUP]
                            enable comment markup parsing and reflow
      --first-comment-is-literal [FIRST_COMMENT_IS_LITERAL]
                            If comment markup is enabled, don't reflow the first
                            comment block in eachlistfile. Use this to preserve
                            formatting of your copyright/licensestatements.
      --literal-comment-pattern LITERAL_COMMENT_PATTERN
                            If comment markup is enabled, don't reflow any comment
                            block which matchesthis (regex) pattern. Default is
                            `None` (disabled).
      --fence-pattern FENCE_PATTERN
                            Regular expression to match preformat fences in
                            comments default=r'^\s*([`~]{3}[`~]*)(.*)$'
      --ruler-pattern RULER_PATTERN
                            Regular expression to match rulers in comments
                            default=r'^\s*[^\w\s]{3}.*[^\w\s]{3}$'
      --emit-byteorder-mark [EMIT_BYTEORDER_MARK]
                            If true, emit the unicode byte-order mark (BOM) at the
                            start of the file
      --hashruler-min-length HASHRULER_MIN_LENGTH
                            If a comment line starts with at least this many
                            consecutive hash characters, then don't lstrip() them
                            off. This allows for lazy hash rulers where the first
                            hash char is not separated by space
      --canonicalize-hashrulers [CANONICALIZE_HASHRULERS]
                            If true, then insert a space between the first hash
                            char and remaining hash chars in a hash ruler, and
                            normalize it's length to fill the column
      --input-encoding INPUT_ENCODING
                            Specify the encoding of the input file. Defaults to
                            utf-8.
      --output-encoding OUTPUT_ENCODING
                            Specify the encoding of the output file. Defaults to
                            utf-8. Note that cmake only claims to support utf-8 so
                            be careful when using anything else

.. tag: usage-end
