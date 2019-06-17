====================
Formatting Algorithm
====================

The formatter works by attempting to select an
appropriate ``position`` and ``wrap`` (collectively referred to as a
"layout") for each node in the layout tree. Positions are represented by
``(row, col)`` pairs and the wrap dictates how childen of that node
are positioned.

--------
Wrapping
--------

``cmake-format`` implements two styles of wrapping:

Horizontal Wrapping
===================

Horizontal wrapping is like "word wrap". Each child is assigned a position
immediately following it's predecessor, so long as that child fits in the
remaining space up to the column limit. Otherwise the child is moved to the
next line::

    |                       |<- col-limit
    | ██████ ███ ██ █████   |
    | ███████████████ ████  |
    | █████████ ████        |

Note that a line comment can force an early newline::

    |                       |<- col-limit
    | ██████ ███ #          |
    | ██ █████              |
    | ███████████████ ████  |
    | █████████ ████        |

Note that wrapping happens at the depth of the layout tree, so if we have
multiple groups of multiple arguments each, then each group will be placed
as if it were a single unit::

    |                               |<- col-limit
    | (██████ ███) (██ █████)       |
    | (███ ██ ███████████████ ████) |

Groups may be parenthetical groups (as above) or keyword groups::

    |                               |<- col-limit
    | ▒▒▒▒▒▒▒ ███ ▒▒▒ █████         |
    | ▒▒▒▒▒ ██ ███████████████ ████ |

or any other grouping assigned by the parser.

In the event that a subgroup cannot be packed within a single line of full
column width, it will be wrapped internally, and the next group placed on
the next line::

    |                               |<- col-limit
    | ▒▒▒▒▒ ███ ▒▒▒▒ █████          |
    | ▒▒▒▒ ██ ███████████████ ████  |
    |      ██ █████                 |
    | ▒▒▒▒▒▒▒ ██ ██ █ ▒▒ █          |

In particular the following is never a valid packing (where the two groups are
siblings) in the layout tree::

    |                               |<- col-limit
    | ▒▒▒ █████ ▒▒▒ ██              |
    |               ███████████████ |
    |               ████ ██ █████   |

Vertical Wrapping
=================

Vertical wrapping assigns each child to the next row::

    ██████
    ███
    ██
    █████
    ███████████████
    ████

Again, note that this happens at the depth of the layout tree. In particular
children may be wrapped horizontally internally::

    | ▒▒▒▒▒▒ ███ ██████       |<- col-limit
    | ▒▒▒ ██████ ██           |
    | ▒▒▒▒ ████ █████ ██████  |
    |      ██████ ██████      |
    |      ████ ██████████    |
    | ▒▒ ███ ████             |

-------
Nesting
-------

In addition to wrapping, ``cmake-format`` also must decide how to nest children
of a layout node.

Horizontal Nesting
==================

Horizontal nesting places children in a column immediately following the
terminal cursor of the parent. For example::

    |                       |<- col-limit
    | ▒▒▒ ██ ███ ██ █████   |
    |     ████████████████  |
    |     █████████ ████    |

In a more deeply nested layout tree, we might see the following::

    |                           |<- col-limit
    | ▓▓▓ ▒▒▒ ██ ███ ██ █████   |
    |         ████████████████  |
    |         █████████ ████    |
    |     ▒▒▒ ████ ███ █        |
    |     ▒▒▒▒▒▒ ████ ███ █     |

Vertical nesting
================

Vertical nesting places children in a column which is one tabwidth to the
right of the parent node's position, and one line below. For example::

    |                       |<- col-limit
    | ▒▒▒▒▒                 |
    |   ██ ███ ██ █████     |
    |   ████████████████    |
    |   █████████ ████      |

In a more deeply nested layout tree, we might see the following::

    |                           |<- col-limit
    | ▓▓▓▓▓                     |
    |   ▒▒▒▒▒                   |
    |     ██ ███ ██ █████       |
    |     ████████████████      |
    |     █████████ ████        |
    |   ▒▒▒                     |
    |     ████ ███ █            |
    |   ▒▒▒▒▒▒                  |
    |     ████ ███ █            |

Depending on how ``cmake-format`` is configured, elements at different depths
may be nested differently. For example::

    |                           |<- col-limit
    | ▓▓▓▓▓                     |
    |   ▒▒▒▒▒ ██ ███ ██ █████   |
    |         ████████████████  |
    |         █████████ ████    |
    |   ▒▒▒ ████ ███ █          |
    |   ▒▒▒▒▒▒ ████ ███ █       |


--------------------
Formatting algorithm
--------------------

For top-level nodes in the layout tree (i.e. ``COMMENT``, ``STATEMENT``,
``BODY``, ``FLOW_CONTROL``, etc...) the positioning is straight forward and
these nodes are laid out in a single pass. Each child is positioned on the
first line after the output cursor of it's predecessor, and at a column
``config.tab_size`` to the right of it's parent.

``STATEMENTS`` however, are laid out over several passes until the
text for that subtree lies is accepted. Each pass is governed by a
specification mapping node depth to a layout algorithm (i.e. a
``(nesting,wrapping)`` pair, as well as a condition of acceptance.


Ideas
=====

* If the name of the command (plus parenthesis) is less than or equal to
  tab-width then vertical nesting is off the table.
* If the name of the command (plus parenthesis) is "very long" then horizontal
  nesting is off the table.
* If a PARGGROUP is a "list" then we should probably have some options for
  deciding whether or not it is wrapped horizontally or vertically:

  * vertical wrap if number of arguments > some threshold
  * wrap always
  * wrap always for specific statments/kwargs/paths

* Multiple KWARGGROUPS should always be nested vertically (optionally)
* Can implement that guys idea about column-aligning kwarg arguments,
  perhaps if kwargs are within some threshold of the same size
* If a statement interior ends with a comment we must dangle the parenthesis
* configuration to decide whether or not to dangle a parenthesis always
* Algorithm order for PARGGROUP (currently)::

    (nest:H, wrap:H), valid if numlines == 1
    (nest:H, wrap:V), valid if columns are not exceeded
    (nest:V, wrap:V)

* I think that I might prefer::

    (nest:H, wrap:H), valid if numlines <= [config-option=1]
    (nest:V, wrap:H), valid if numlines <= [config-option=1]
    (nest:V, wrap:V)

* Algorithm order for ARGGROUP with at least [n=2] KWARGGROUPS:

    (nest:H, wrap:H), valid if numlines < [config-option=0] (i.e. never)
    (nest:V, wrap:V),

* So should we use some kind of overridable function to get
* If we do limit HWRAP to at most 2 lines, are there any cases where this
  would do something we don't want? Generally we don't have lots of
  unstructured positional arguments that aren't lists. Also, if we had
  such a thing, could we not tag it that way?


Positional Arguments
====================

Candidate algorithm:

First, wrap horizontally. If they all fit on [n=2] lines, and if the
statement spelling does not exceed [k=2] characters above the tab-width, choose
that layout. Note that the previous rule can be enforced by this rule with
[n=1], so perhaps we can exclude a special case for the previous attempt::

    foobarbaz_hello(argument_one argument_two argument_three argument_four
                    argument_five argument_six)

If not, nest vertically, and if they fit on [n=2] lines, choose that layout::

    foobarbaz_hello(
        argument_one argument_two argument_three argument_four argument_five
        argument_six)

Note that, if the statement spelling (plus optional space and paren) are less
than the tab width, then vertical nesting is disabled. In which case we proceed
directly to the next attempt: vertical wrap::

    foobarbaz_hello(
        argument_one
        argument_two
        argument_three
        argument_four
        argument_five
        argument_six)

In order to match expectation and current behavior, I think by default we can
use values of (2, 2) but I think that personally I will want values of (1,1).
We can describe this sequence by the following escallation of attempts. If
each attempt fails we move onto the nest.

1. initially horizontal nesting, horizontal wrapping
2. switch to vertical nesting, if allowed
3. switch to vertical wrapping if allowed

This differs a little from the current algorithm and I'm not sure what the best
way to unify them is, perhaps it's to continue
specifying an "algorithm order" kind of thing. We could change it to
something like:

0. ``(vertical-nest, vertical-wrap)``
1. ``(False, False)``
2. ``(False, True)``
3. ``(True, False)``
4. ``(True, True)``

And then pair each with a configurable approval function. For instance I would
always reject #2. The problem here is that for short statement names like
``set()`` or for large tab-widths, vertical nesting is not allowed. Perhaps
that is just something we need to specify in the approval function though. For
what I want personally, The approval function for #2 would be to reject always
unless the statement spelling too small to vertically wrap.

Note also, though, that my desired algorithm order is not consistent at depth.
I generally want to avoid #2 for statement groups, but I generally want to
avoid #3 for keyword groups. And how about deeply nested kwarg groups?

Comments
========

A (multi-line) comment on the last row does not contribute to the height for
the purposes of this thresholding, but one on any other line does. Another way
to say this is that comments are excluded from the size computation, but
their influence on other argument is not::

    # This content is 3 lines tall
    foobarbaz_hello(▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
       ▏argument_one argument_two # this comment is two lines long and it   ▕
       ▏                          # forces the next argument onto line three▕
       ▏argument_three argument_four)                                       ▕
       ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
    # This is only 2 lines tall
    foobarbaz_hello(▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
       ▏argument_one argument_two argument_three▕
       ▏argument_four # this comment is two lines long and wraps but it
       ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔# has no contribution to the size of the content.

Dealing with comments during horizontal wrapping can be a little tricky.
They definitely induce a newline at their termination, but they may also
predicate a newline in front of the commented argument. See the examples in
:ref:`Case Studies/Comments <comments-case-study>`. We don't necessarily need
to deal with this right now. The user can always force the issue by adding some
comment strings that force a comment width, like this::

    set(HEADERS header_a.h header_b.h header_c.h
        header_d.h # This comment is pretty long and if it's argument is close
                   # to the edge of the column then the comment gets wrapped
                   # very poorly ------------------------
        header_e.h header_f.h)

The string of dashes ``------------------------`` is long enough that the
minimum width of the comment block is given by::

    # This comment is pretty
    # long and if it's
    # argument is close to the
    # edge of the column then
    # the comment gets wrapped
    # very poorly
    # ------------------------

Which would preclude it from being crammed into the right-most slot.

Special-case Positional Arguments
=================================

There are some situations in which we might want to apply a different threshold
set than the default. ``COMMAND`` kwargs in particular we probably never want
to wrap vertically.

Interior groups
===============

Keyword subtrees (``KWARGGROUP``) themselves are laid out the same as
statements, but interior nodes (``ARGGROUP``) in the parse/layout tree follow
a slightly different set of rules. The reasoning for this separate rule set is
that the syntatic boundary between children in an ``ARGGROUP`` are also
significant semantic boundaries and so breaking a line on these boundaries is
cheaper than breaking a line within a positional argument group.

Candidate Algorithm:

Wrap horizonally, if they all fit on [n=1] lines and if there are at most [n=2]
non-empty groups. For example::

    foobarbaz_hello(argument_one argument_two KEYWORD_ONE kwarg_one)

Otherwise, nest vertically, if they all fit on [n=1] lines and if there are
at most [n=2] non-empty groups::

    foobarbaz_hello(
      argument_one argument_two argument_three KEYWORD_ONE kwarg_one kwarg_two)

Otherwise, wrap vertically::

    foobarbaz_hello(
      argument_one argument_two argument_three
      KEYWORD_ONE kwarg_one kwarg_two
      KEYWORD_TWO kwarg_three kwarg_four)

------------
Search Order
------------

The current algorithm does a kind of top-down implementation. Each node is
allowed to try layouts in "algorithm order" from start up to their parent's
current algorithm. This seems to work well even for
:ref:`deeply nested <install-case-study>` or
:ref:`complex <conditionals-case-study>` statements.
