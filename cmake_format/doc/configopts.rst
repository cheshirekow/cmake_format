.. _configopts:

======
global
======

include
=======

``include`` specifies a list of additional configuration files to load.
Configurations are merged and individual variables follow a latest-wins
semantic.

-----
parse
-----

additional_commands
===================

Use this variable to specify how to parse custom cmake functions.
See :ref:`additional-cmd`.

vartags
=======

Specify a mapping of variable patterns (python regular expression) to a list
of tags. Any time a a variable matching this pattern is encountered the tags
can be used to affect the parsing/formatting. For example:

.. code::

   vartags = [
     (".*_COMMAND", ["cmdline"])
   ]

Specifies that any variable ending in ``_COMMAND`` be tagged as ``cmdline``.
This will affect the formatting by preventing the arguments from being
vertically wrapped.

Note: this particular rule is builtin so you do not need to include this in
your configuration. Use the configuration variable to add new rules.

proptags
========

Specify a mapping of property patterns (python regular expression) to a list
of tags. Any time a a property matching this pattern is encountered the tags
can be used to affect the parsing/formatting. For example:

.. code::

   proptags = [
     (".*_DIRECTORIES", ["file-list"])
   ]

Specifies that any property ending in ``_DIRECTORIES`` be tagged as
``file-list``. In the future this may affect formatting by allowing arguments
to be sorted (but currently has no effect).

Note: this particular rule is builtin so you do not need to include this in
your configuration. Use the configuration variable to add new rules.

------
format
------

line_width
==========

``line_width`` specifies the number of columns that ``cmake-format`` should
fit commands into. This is the number of columns at which arguments will be
wrapped.

.. code::

  # line_width = 80 (default)
  add_library(libname STATIC sourcefile_one.cc sourcefile_two.cc
                             sourcefile_three.cc sourcefile_four.cc)

  # line_width = 100
  add_library(libname STATIC sourcefile_one.cc sourcefile_two.cc sourcefile_three.cc
                             sourcefile_four.cc)

tab_size
========

``tab_size`` indicates how many spaces should be used to indent nested
"scopes". For example:

.. code::

  # tab_size = 2 (default)
  if(this_condition_is_true)
    message("Hello World")
  endif()

  # tab_size = 4
  if(this_condition_is_true)
      message("Hello World")
  endif()


max_subgroups_hwrap
===================

A "subgroup" in this context is either a positional or keyword argument group
within the current depth of the statement parse tree. If the number of
"subgroups" at this depth is greater than ``max_subgroups_hwrap`` then
hwrap-formatting is inadmissable and a vertical layout will be selected.

The default value for this parameter is `2`.

Consider the following two examples:

.. code:: cmake

  # This statement has two argument groups, so hwrap is admissible
  add_custom_target(target1 ALL COMMAND echo "hello world")

  # This statement has three argument groups, so the statement will format
  # vertically
  add_custom_target(
     target2 ALL
     COMMAND echo "hello world"
     COMMAND echo "hello again")

In the first statement, there are two argument groups. We can see them with
``--dump parse``

.. code::

  └─ BODY: 1:0
    └─ STATEMENT: 1:0
        ├─ FUNNAME: 1:0
        ├─ LPAREN: 1:17
        ├─ ARGGROUP: 1:18
        │   ├─ PARGGROUP: 1:18  <-- group 1
        │   │   ├─ ARGUMENT: 1:18
        │   │   └─ FLAG: 1:26
        │   └─ KWARGGROUP: 1:30  <-- group 2
        │       ├─ KEYWORD: 1:30
        │       └─ ARGGROUP: 1:38
        │           └─ PARGGROUP: 1:38
        │               ├─ ARGUMENT: 1:38
        │               └─ ARGUMENT: 1:43
        └─ RPAREN: 1:56

The second statement has three argument groups:

.. code::

  └─ BODY: 1:0
      └─ STATEMENT: 1:0
          ├─ FUNNAME: 1:0
          ├─ LPAREN: 1:17
          ├─ ARGGROUP: 2:5
          │   ├─ PARGGROUP: 2:5  <-- group 1
          │   │   ├─ ARGUMENT: 2:5
          │   │   └─ FLAG: 2:13
          │   ├─ KWARGGROUP: 3:5  <-- group 2
          │   │   ├─ KEYWORD: 3:5
          │   │   └─ ARGGROUP: 3:13
          │   │       └─ PARGGROUP: 3:13
          │   │           ├─ ARGUMENT: 3:13
          │   │           ├─ ARGUMENT: 3:18
          │   └─ KWARGGROUP: 4:5  <-- group 3
          │       ├─ KEYWORD: 4:5
          │       └─ ARGGROUP: 4:13
          │           └─ PARGGROUP: 4:13
          │               ├─ ARGUMENT: 4:13
          │               └─ ARGUMENT: 4:18
          └─ RPAREN: 4:31

max_pargs_hwrap
===============

This configuration parameter is relavent only to positional argument groups.
A positional argument group is a list of "plain" arguments. If the number of
arguments in the group is greater than this number, then then hwrap-formatting
is inadmissable and a vertical layout will be selected.

The default value for this parameter is 6

Consider the following two examples:

.. code::

  # This statement has six arguments in the second group and so hwrap is
  # admissible
  set(sources filename_one.cc filename_two.cc filename_three.cc
              filename_four.cc filename_five.cc filename_six.cc)

  # This statement has seven arguments in the second group and so hwrap is
  # inadmissible
  set(sources
      filename_one.cc
      filename_two.cc
      filename_three.cc
      filename_four.cc
      filename_five.cc
      filename_six.cc
      filename_seven.cc)

max_rows_cmdline
================

``max_pargs_hwrap`` does not apply to positional argument groups for shell
commands. These are never columnized and always hwrapped. However, if the
wrapped format exceeds this many lines, then the group will also be nested.

separate_xxx_with_space
=======================

The two parameters:

* separate_ctrl_name_with_sapce
* separate_fn_name_with_space

dictate whether or not to insert a space between a statement command name and
the corresponding left parenthesis. For example:

.. code::

  # separate_ctrl_name_with_space = True
  if (condition)
    # ... do something
  endif ()

  # separate_ctrl_name_with_space = False (default)
  if(condition)
    # ... do something
  endif()

``separate_ctrl_name_with_space`` applies to control flow statements such as
``if`` and ``foreach`` whereas ``separate_fn_name_with_space`` applies to
everything else. You may want to use separate values for these two since
control flow statements are often composed of boolean logic and so the extra
space may help readability in some cases. The default value is ``False`` for
both.

dangle_parens
=============

If a statement is wrapped to more than one line, than dangle the closing
parenthesis on its own line. For example:

.. code::

  # dangle_parens = False (default)
  set(sources filename_one.cc filename_two.cc filename_three.cc
              filename_four.cc filename_five.cc filename_six.cc)

  # dangle_parens = True
  set(sources filename_one.cc filename_two.cc filename_three.cc
            filename_four.cc filename_five.cc filename_six.cc
  )  # <-- this is a dangling parenthesis

The default is ``false``.

dangle_align
============

If the trailing parenthesis must be 'dangled' on it's on line, then align it
to this reference. Options are:

* ``prefix``: the start of the statement,
* ``prefix-indent``: the start of the statement, plus one indentation  level
* ``child``: align to the column of the arguments

For example:

.. code::

  # dangle_align = "prefix"
  set(sources filename_one.cc filename_two.cc filename_three.cc
           filename_four.cc filename_five.cc filename_six.cc
  )  # <-- aligned to the statement

  # dangle_align = "prefix-indent"
  set(sources filename_one.cc filename_two.cc filename_three.cc
           filename_four.cc filename_five.cc filename_six.cc
    )  # <-- plus one indentation level

  # dangle_align = "child"
  set(sources filename_one.cc filename_two.cc filename_three.cc
           filename_four.cc filename_five.cc filename_six.cc
      )  # <-- aligned to "sources"


layout_passes
=============

See the :ref:`Formatting Algorithm <formatting-algorithm>` section for more
information on how `cmake-format` uses multiple passes to converge on the
final layout of the listfile source code. This option can be used to override
the default behavior. The format of this option is a dictionary, where the keys
are the names of the different layout node classes:

* StatementNode
* ArgGroupNode
* KWargGroupNode
* PargGroupNode
* ParenGroupNode

The dictionary values are a list of pairs (2-tuples) in the form of
:code:`(passno, wrap-decision)`. Where :code:`passno` is the pass number at
which  the wrap-decision becomes active, and :code:`wrap-decision` is a boolean
:code:`(true/false)`. For each layout pass, the decision of whether or not the
node should wrap (either nested, or vertical) is looked-up from this map.

min_prefix_chars
================

This value only comes into play when considering whether or not to nest
arguments below their parent. If the number of characters in the parent is
less than this value, we will not nest. In the example below, we'll set
``line_width=40`` for illustration:

.. code::

  # min_prefix_chars = 4 (default)
  message(
    "With the default value, this "
    "string is allowed to nest beneath "
    "the statement")

  # min_prefix_chars = 8
  message("With the default value, this "
          "string is allowed to nest beneath "
          "the statement")

max_lines_hwrap
===============

Usually the layout algorithm will prefer to do a simple "word-wrap" of
positional arguments, if it can. However if such a simple word-wrap would
exceed this many lines, then that layout is rejected, and further passes are
tried. The default value is ``max_lines_hwrap=2`` so, for example:

.. code::

  message("This message can easily be wrapped" "to two lines so there is no"
          "problem with using" "horizontal wrapping")
  message(
    "However this message cannot be wrapped to two lines because the "
    "arguments are too long. It would require at least three lines."
    "As a result, a simple word-wrap is rejected"
    "And each argument"
    "gets its own line")

line_ending
===========

This is a string indicating which style of line ending ``cmake-format`` should
use when writing out the formatted file. If ``line_ending="unix"`` (default)
then the output will contain a single newline character (``\n``) at the end of
each line. If ``line_ending="windows"`` then the output will contain a
carriage-return and newline pair (``\r\n``). If ``line_ending="auto"`` then
``cmake-format`` will observe the first line-ending of the input file and will
use style that all lines in the output.

command_case
============

``cmake`` ignores case in command names. Very old projects tend to use
uppercase for command names, while modern projects tend to use lowercase.
There are three options for this variable:

* ``upper``: format commands as uppercase
* ``lower``: format commands as lowercase
* ``canonical``: format standard commands as they are formatted in the
  ``cmake`` documentation.

``canonical`` is generally the same as ``lower`` except that some third-party
find modules that have moved into the distribution (e.g.
``ExternalProject_Add``).

keyword_case
============

``cmake`` ignores the case of sentinal words (keywords) in argument lists.
Generally projects tend to prefer uppercase (``keyword_case="upper"``) which is
the default. Alternatively, this may also be set to ``lower`` to format
keywords as lowercase.

require_valid_layout
====================

By default, if cmake-format cannot successfully fit everything into the
desired linewidth it will apply the last, most agressive attempt that it made.
If this flag is True, however, cmake-format will print error, exit with non-
zero status code, and write-out nothing


-------
comment
-------

bullet_char
===========

When cmake-format parses and reflows comment text, this is the character that
it looks for and emits for unordered bulleted lists. The default is the
asterisk character (``*``). For example:

.. code::

   # * one
   # * two
   # * three


enum_char
=========

When cmake-format parses and reflows comment text, this is the character that
it looks for and emits after the numeral for ordered bulleted lists. The
default is the period character (``.``). For example:

.. code::

   # 1. foo
   # 2. bar
   # 3. baz

first_comment_is_literal
========================

Don't reflow the first comment block in each listfile. Use this to preserve
formatting of your copyright/license statements. shebang lines are always
preserved and are not considered the first comment for the purpose of
implementing this feature.

literal_comment_pattern
=======================

Don't reflow any comment block which matches this (regex) pattern. Default is
`None` (disabled). This can be used to match e.g. standard copyright text that
shouldn't be reflowed. The format is a python regular expression.

fence_pattern
=============

``cmake-format`` supports fenced literals in comments. Any comment text
between a pair of fences is preserved verbatim without reformatting. The
pattern of characters that defines a fence is defined by this variable. The
format is a python regular expression. The default is
``^\s*([`~]{3}[`~]*)(.*)$`` which will match three or more backticks
(:literal:`\`\`\``) or tilde (``~~~``) characters. e.g.

.. code::

  # This is paragraph text but:
  # ```
  #    This
  # is
  #      some literal text
  # ```

ruler_pattern
=============

``cmake-format`` will attempt to recognize and canonicalize "rulers" within
comment text. A ruler is a sequence of characters used to intentionally break
up text, such as the following:

.. code::

  # Section Title
  # =============
  # Paragraph text

In this example, the sequence of equals (``=``) characters is used as a
"ruler". The definition of what constitutes a ruler is stored in this variable.
The format is a python regular expression pattern. The default value is
``^\s*[^\w\s]{3}.*[^\w\s]{3}$`` which will match any sequence of three or more
special characters on either side of anything (in the case of nothing
in-between, this means at least six special characters). This pattern will
match, e.g. the following:

.. code::

  # ======
  # === ===
  # === Some Text ===
  # ___ Some Text ___

hashruler_min_length
====================

Because the hash character (``#``) has syntax in cmake, rulers (see above)
that are composed of hash characters are dealt with a little differently.
In general ``cmake-format`` will chomp multiple hash characters as un-intended
redundancy, unless the sequence contains at least this many characters.
The default is ``10``.

canonicalize_hashrulers
=======================

If true, then insert a space between the first hash char and remaining hash
chars in a hash ruler, and normalize its length to fill the column

enable_markup
=============

This is the big on/off switch for comment reflow and formatting. If this is
``true`` (the default) then ``cmake-format`` comment processing and formatting
features are enabled. If ``false``, then comments are generally preserved,
but trailing whitespace will still be removed.

explicit_trailing_pattern
=========================

If ``cmake-format`` encountes a comment within or at the very end of a
statement it will try to determine whether or not that comment refers to
a particular argument, and will format it accordingly. For example:

.. code::

  cmake_parse_arguments(
    ARG
    "FOO BAR" # optional keywords
    "BAZ" # one value keywords
    "BOZ" # multi value keywords
    ${ARGN})

The rules for associating a comment with the preceeding argument depend on
how much (and what kinds) of whitespace separate them. Alternatively, if
the comments match the ``explicit_trailing_pattern``, then they are associated
with the preceeding argument regardless of the whitespace separating them.
The format for this variable is a python regular expression matching prefix
characters for such explicit trailing comments. The default value is ``#<``,
such that the above example using explicit trailing comments would  be:

.. code::

  cmake_parse_arguments(
    ARG
    "FOO BAR" #< optional keywords
    "BAZ" #< one value keywords
    "BOZ" #< multi value keywords
    ${ARGN})

------
encode
------

emit_byteorder_mark
===================

If ``true`` (the default is ``false``) then output the unicode byte-order at
the start of the document.

input_encoding
==============

Specify the input encoding of the file. The format of this string is `anything
understood`__ by the ``encoding=`` keyword of the python ``open()`` function.
The default is ``utf-8``.

.. __: https://docs.python.org/3/library/codecs.html#standard-encodings

output_encoding
===============

Specify the output encoding of the file. The format of this string is `anything
understood`__ by the ``encoding=`` keyword of the python ``open()`` function.
The default is ``utf-8``.

.. __: https://docs.python.org/3/library/codecs.html#standard-encodings
