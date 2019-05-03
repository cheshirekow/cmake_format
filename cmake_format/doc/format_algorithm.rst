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

