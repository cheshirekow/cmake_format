.. _configopts:

=====================
Configuration Options
=====================

--------------------------
General Formatting Options
--------------------------

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

separate_xxx_with_space
=======================

The two parameters:

* separate_ctrl_name_with_sapce
* separate_fn_name_with_space

Dictate whether or not to insert a space between a statement command name and
the corresponding left parenthesis. For example:

.. code::

  # separate_ctrl_name_with_space = True
  if (condition)
    # ... do something
  endif ()

.. code::

  # separate_ctrl_name_with_space = False
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

  # dangle_parens = False
  set(sources filename_one.cc filename_two.cc filename_three.cc
              filename_four.cc filename_five.cc filename_six.cc)

.. code::

  # dangle_parens = True
  set(sources filename_one.cc filename_two.cc filename_three.cc
            filename_four.cc filename_five.cc filename_six.cc
  )  # <-- this is a dangling parenthsis

The default is false

dangle_align
============

If the trailing parenthesis must be 'dangled' on it's on line, then align it
to this reference. Options are:

* ``prefix``: the start of the statement,
* ``prefix-indent``: the start of the statement, plus one indentation  level
* ``child``: align to the column of the arguments

For example:

.. code::

  # dangle_align = prefix
  set(sources filename_one.cc filename_two.cc filename_three.cc
           filename_four.cc filename_five.cc filename_six.cc
  )  # <-- aligned to the statement

.. code::

  # dangle_align = prefix-indent
  set(sources filename_one.cc filename_two.cc filename_three.cc
           filename_four.cc filename_five.cc filename_six.cc
    )  # <-- plus one indentation level

.. code::

  # dangle_align = child
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
