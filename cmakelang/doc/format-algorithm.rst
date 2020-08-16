.. _formatting-algorithm:

====================
Formatting Algorithm
====================

The formatter works by attempting to select an appropriate ``position`` and
``wrap`` (collectively referred to as a "layout") for each node in the layout
tree. Positions are represented by ``(row, col)`` pairs and the wrap dictates
how childen of that node are positioned.

--------
Wrapping
--------

``cmake-format`` implements three styles of wrapping.
The default wrapping for all nodes is horizontal wrapping. If horizontal
wrapping fails to emit an admissible layout, then a node will advance to
either vertical wrapping or nested wrapping (which one depends on the type of
node).

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
children may be wrapped horizontally within the subtrees::

    | ▒▒▒▒▒▒ ███ ██████       |<- col-limit
    | ▒▒▒ ██████ ██           |
    | ▒▒▒▒ ████ █████ ██████  |
    |      ██████ ██████      |
    |      ████ ██████████    |
    | ▒▒ ███ ████             |


Nesting
=======

Nesting places children in a column which is one ``tab_width`` to the
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

Note that the only nodes that can nest are ``STATEMENT`` and ``KWARGGROUP``
nodes. These nodes necessarily only have one child, an ``ARGGROUP`` node.
Therefore there really isn't a notion of "wrapping" for these nodes.

--------------------
Formatting algorithm
--------------------

For top-level nodes in the layout tree (i.e. ``COMMENT``, ``STATEMENT``,
``BODY``, ``FLOW_CONTROL``, etc...) the positioning is straight forward and
these nodes are laid out in a single pass. Each child is positioned on the
first line after the output cursor of it's predecessor, and at a column
``config.format.tab_size`` to the right of it's parent.

``STATEMENTS`` however, are laid out over several passes until the
text for that subtree is accepted. Each pass is governed by a
specification mapping pass number to a wrap decision (i.e. a
boolean indicating whether or not to wrap vertical or nest children)

Layout Passes
=============

The current algorithm works in a kind of top-down refinement. When a node is
laid out by calling it's ``reflow()`` method, it is informed of its parent's
current pass number (``passno``). It then iterates through its own ``passno``
from zero up to it's parent's ``passno`` and terminates at the first admissible
layout. Note that within the layout of the node itself, it's current
``passno`` can only affect its ``wrap`` decision. However, because each of its
children will advance through their own passes, the overall layout of a subtree
between two different passes may change, even if the node at the subtree root
didn't change it's ``wrap`` decision between those passes.

This approach seems to work well even for
:ref:`deeply nested <install-case-study>` or
:ref:`complex <conditionals-case-study>` statements.

Newline decision
================

When a node is in horizontal layout mode (``wrap=False``), there are a couple
of reasons why the algorithm might choose to insert a newline between two
of it's children.

1. If a token would overflow the column limit, insert a newline (e.g. the
   usual notion of wrapping)
2. If the token is the last token before a closing parenthesis, and the
   token plus the parenthesis would overflow the column limit, then insert a
   newline.
3. If a token is preceeded by a line comment, then the token cannot be placed
   on the same line as the comment (or it will become part of the comment) so
   a newline is inserted between them.
4. If a token is a line comment which is not associated with an argument (e.g.
   it is  a "free" comment at the current scope) then it will not be placed
   on the same line as a preceeding argument token. If it was, then subsequent
   parses would associate this comment with that argument. In such a case, a
   newline is inserted between the preceeding argument and the line comment.
5. If the node is an interior node, and one of it's children is internally
   wrapped (i.e. consumes more than two lines) then it will not be placed
   on the same line as another node. In such a case a newlines is inserted.
6. If the node is an interior node and a child fails to find an admissible
   layout at the current cursor, a newline is inserted and a new layout attempt
   is made for the child.

Admissible layouts
==================

There are a couple of reasons why a layout may be deemed inadmissible:

1. If the bounding box of a node overflows the column limit
2. If a node is horizontally wrapped at the current ``passno`` but consumes
   more than ``max_lines_hwrap`` lines
3. If the node is horizontally wrapped at the current ``passno`` but the node
   path is marked as ``always_wrap``

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

