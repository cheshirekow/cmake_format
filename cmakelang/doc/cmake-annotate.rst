.. _render_html:

==============
cmake-annotate
==============

The ``cmake-annotate`` frontend
program which can create semantic HTML documents from parsed listfiles.
This enables, in particular, semantic highlighting for your
code documentation.

.. literalinclude:: bits/annotate-usage.txt

``--format stub`` will output just the marked-up listfile content. The
markup is done as ``<span>`` elements with different css classes for each
parse-tree node or lexer token. The content is not encapsulated in any root
element (such as a ``<div>``). ``--format page`` will embed that content
into a full page with a root ``<html>`` and an embedded stylesheet.

The example listfile in the README, for example, can be rendered as:

.. raw:: html
   :file: example_rendered.html
