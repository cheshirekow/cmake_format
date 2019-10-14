=====================
Configuration Options
=====================

-------------
layout_passes
-------------

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
