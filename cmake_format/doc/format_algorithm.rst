====================
Formatting Algorithm
====================

As of version ``0.4.0`` the formatter works by attempting to select an
appropriate ``position`` and ``wrap`` algorithm for each node in the layout
tree. Positions are represented by ``(row, col)`` pairs and ``wrap`` algorithms
dictate how childen of that node are positioned.

Each node in the layout tree implements a ``reflow`` method taking as input
an immutable configuration object, a cursor (i.e. ``(row, column)`` pair),
and a pass number (``passno``).

For top-level nodes in the layout tree (i.e. ``COMMENT``, ``STATEMENT``,
``BODY``, ``FLOW_CONTROL``, etc...) the positioning is straight forward and
these nodes are laid out in a single pass. Each child is positioned on the
first line after the output cursor or it's predecessor, and at a column
corresponding to it's ``depth`` times ``config.tab_size``.

``STATEMENTS`` however, are ``reflow()``ed over several passes (incrementing
``passno`` each time) until they satisfy formatting requirements. At this point
there is only one implemented formatting requirement: all text must be
kept within the column limit. The design, however, will hopefully allow for
other formatting requirements dictated by a projects styleguide.

At each pass of ``reflow`` the ``STATEMENT`` node will advance it's wrap
algorithm. The wrap algorithm dictates how children are positioned with respect
to the parent (``STATEMENT``) node. The wrap algorithm is finalized on the
pass when the ``STATEMENT`` first fits within the column limit (starting at)
it's position.

Children of the ``STATEMENT`` are (recursively) ``reflow()``-ed themselves. They
are laid out over several passes, starting with the initial wrap algorithm, up
to the current wrap algorithm of it's parent. In this way nodes in the tree
are hierarchically ``reflow()``-ed until everything fits.

===============
Wrap Algorithms
===============

On each successive pass of ``reflow()`` a node will lay out it's children
using a different wrap algorithm. These algorithms are ordered in a sense of
"aggressiveness" so that at each pass we get more agressive with how we wrap
children.

-----
HPACK
-----

The initial wrap algorithm is horizontal packing (``HPACK``), which simply
assigns to each child a position immediately following it's predecessor.
Consider, for example, a keyword argument which is composed of a keyword and
eight associated arguments. It's ``HPACK`` layout may look like this::

    ████ ██████ ███ ██ █████ ███████████████ ████ █████████ ████

-----
VPACK
-----

If a horizontal layout for this node exceeds the configured column limit, then
the wrap algorithm may be advanced to a vertical packing (i.e. ``wrap=VPACK``)
which would might result in the following layout::

    ████ ██████
         ███
         ██
         █████
         ███████████████
         ████
         █████████
         ████

Note that any comments in an argument list (either line comments or argument
comments) will invalidated the ``HPACK`` algorithm and force the node to
``reflow()`` with a vertical packing.

------
NVPACK
------

If, after vertical packing, the node still exceeds the configured column limit,
it will be advanced to "nested vertical" layout (``wrap=NVPACK``), which might
result in the following layout:

    ████
      ██████
      ███
      ██
      █████
      ███████████████
      ████
      █████████
      ████

In general, the vertical layouts assign child positions on the next line after
each child, with one exception. Leaf nodes (i.e. ``ARGUMENT`` nodes) with no
embedded comments may be packed sequentially (i.e. ``HPACK`` ed). So a keyword
argument group with one level of additional nested may be ``VPACKED`` as
follows (where the bottom two rows are positional ``ARGUMENT`` nodes)::

    ████
      ██████ ███
             ██
             █████
      ████ ████
           ██
           ████
      ███ █████ █████ ████
      ████████ ████ ██ ███

