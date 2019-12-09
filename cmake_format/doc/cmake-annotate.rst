.. _render_html:

==============
cmake-annotate
==============

The ``cmake-annotate`` frontend
program which can create semantic HTML documents from parsed listfiles.
This enables, in particular, semantic highlighting for your
code documentation.

.. dynamic: annotate-usage-begin

.. code:: text

    usage:
    cmake-annotate [-h]
                 [--format {page,stub}]
                 [-o OUTFILE_PATH]
                 [-c CONFIG_FILE]
                 infilepath [infilepath ...]

    Parse cmake listfiles and re-emit them with semantic annotations in HTML.

    Some options regarding parsing are configurable by providing a configuration
    file. The configuration file format is the same as that used by cmake-format,
    and the same file can be used for both programs.

    cmake-format can spit out the default configuration for you as starting point
    for customization. Run with `--dump-config [yaml|json|python]`.

    positional arguments:
      infilepaths

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -f {page,stub}, --format {page,stub}
                            whether to output a standalone `page` complete with
                            <html></html> tags, or just the annotated content
      -o OUTFILE_PATH, --outfile-path OUTFILE_PATH
                            Where to write the formatted file. Default is stdout.
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            path to configuration file

    Formatter Configuration:
      Override configfile options

.. dynamic: annotate-usage-end

``--format stub`` will output just the marked-up listfile content. The
markup is done as ``<span>`` elements with different css classes for each
parse-tree node or lexer token. The content is not encapsulated in any root
element (such as a ``<div>``). ``--format page`` will embed that content
into a full page with a root ``<html>`` and an embedded stylesheet.

The example listfile in the README, for example, can be rendered as:

.. raw:: html
   :file: example_rendered.html
