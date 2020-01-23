========
Features
========

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


---------------
Custom Commands
---------------

Due to the fact that cmake is a macro language, `cmake-format` is, by
necessity, a *semantic* source code formatter. In general it tries to make
smart formatting decisions based on the meaning of arguments in an otherwise
unstructured list of arguments in a cmake statement. `cmake-format` can
intelligently format your custom commands, but you will need to tell it how
to interpret your arguments.

Currently, you can do this by adding your command specifications to the
`additional_commands` configuration variables, e.g.:

.. code::

    # Additional FLAGS and KWARGS for custom commands
    additional_commands = {
      "foo": {
        "pargs": 2,
        "flags": ["BAR", "BAZ"],
        "kwargs": {
          "HEADERS": '*',
          "SOURCES": '*',
          "DEPENDS": '*',
        }
      }
    }

The format is a nested dictionary mapping statement names (dictionary keys)
to `argument specifications`__. For the example specification above, the
custom command would look something like this:

.. code::

   foo(hello world
       HEADERS a.h b.h c.h d.h
       SOURCES a.cc b.cc c.cc d.cc
       DEPENDS flub buzz bizz
       BAR BAZ)


.. __: https://cmake-format.rtfd.io/custom_parsers
