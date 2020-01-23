.. _additional-cmd:

===========================
Implementing Custom Parsers
===========================

------------------------------
Using the simple specification
------------------------------

You can tell the parser how to interpret your custom commands by specifying the
format of their call signature using the ``addtitional_commands`` configuration
variable. The format of the variable is a dictionary (a mapping in JSON/YAML)
where the keys should be the name of the command and the values satisfy the
following (recursive) schema:

.. code::

  POSITIONAL_SPEC = {
    # Number of positional arguments. Can be an integer indicating an exact
    # number of arguments, or a string satisfying the regex:
    # "(\d*)\+?|\*|\?". The semantics of the string:
    #
    #   * "?": zero or one
    #   * "*": zero or more
    #   * "+": one or more
    #   * (\d+): exactly `n` positional arguments (e.g. "3")
    #   * (\d+)\+ : as many positional arguments as available, but at least
    #     `n` (e.g. "3+")
    #
    "nargs": <string,int>,

    # Stores a list of keywords that are treated as positional arguments and
    # included in the positional group, but annotated as keywords for special
    # processing (e.g. case canonicalization).
    "flags": [<string>, ...],

    # Stores a list of tags to apply to this positional argument group. See
    # below for more information on tags.
    "tags": [<string>]

    # If true, then this specification will be repeated indefinitately
    "legacy": <bool>,
  }

  KEYWORD_SPEC = {
    "pargs": [POSITIONAL_SPEC, ...],
    "kwargs": {<string>: KEYWORD_SPEC}
  }

As a shorthand:

* If a keyword specification contains no nested `kwargs` and only one
  positional argument group, you may omit the `KEYWORD_SPEC` overhead and
  write the `POSITIONAL_SPEC` directly (including shorthands below)
* There is only one positional group, you may omit the list
* The a positional contains now flags, and is not tagged, you may omit the
  outer dictionary and write only the `nargs` value.

Tags
====

Positional argument groups support the following tags:

* `cmdline`: The positional arguments of this group are command line arguments
  in a shell command. In particular this means that they will not be wrapped
  vertically
* `file-list`: The positional arguments of this group are names/paths of files.
  In the future this tag will enable certain filters for formatting or linting,
  such as automatic sorting.

--------------------------------
Generating simple specifications
--------------------------------

There is an experimental utility called ``cmake-genparsers`` which can generate
simple specifications for cmake functions and macros that use
``cmake_parse_arguments``. The tool has very limited ability to process cmake
arguments. There is a frontend included in the python distribution. Usage
is

.. code::

  usage:
  cmake-genparsers [-h] [-o OUTFILE_PATH] infilepath [infilepath ...]

  Parse cmake listfiles, find function and macro declarations, and generate
  parsers for them.

  positional arguments:
    infilepaths

  optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -l {error,warning,info,debug}, --log-level {error,warning,info,debug}
    -o OUTFILE_PATH, --outfile-path OUTFILE_PATH
                          Write results to this file. Default is stdout.
    -f {json,yaml,python}, --output-format {json,yaml,python}

For example:

.. code::

  :~$ cmake-genparsers /usr/share/cmake-3.10/Modules/*.cmake
  { 'add_command': {'pargs': {'nargs': 1}},
    'add_compiler_export_flags': {'pargs': {'nargs': 0}},
    'add_feature_info': {'pargs': {'nargs': 3}},
    'add_file_dependencies': {'pargs': {'nargs': 1}},
    'add_flex_bison_dependency': {'pargs': {'nargs': 2}},
    'add_jar': { 'kwargs': { 'ENTRY_POINT': 1,
                            'INCLUDE_JARS': '+',
                            'MANIFEST': 1,
                            'OUTPUT_DIR': 1,
                            'OUTPUT_NAME': 1,
  ...

or

.. code::

  :~$ cmake-genparsers -f yaml /usr/share/cmake-3.10/Modules/*.cmake
  add_file_dependencies:
    pargs:
      nargs: 1
  android_add_test_data:
    pargs:
      nargs: 1+
      flags: []
    kwargs: {}
  get_bundle_main_executable:
    pargs:
  ...

This tool is still in the early stages of development so don't be surprised if
it chokes on some of your input files, or if it does not propery generate
specifications for your commands.
