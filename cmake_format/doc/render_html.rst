.. _render_html:

===========================
HTML Rendering of Listfiles
===========================

There is an experimental utility to create semantic HTML documents from a
parsed listfile. This enables, in particular, semantic highlighting for your
code documentation. Use ``--dump html-stub`` or ``--dump html-page``
command line options to use this feature.

``--dump html-stub`` will output just the marked-up listfile content. The
markup is done as ``<span>`` elements with different css classes for each
parse-tree node or lexer token. The content is not encapsulated in any root
element (such as a ``<div>``). ``--dump html-page`` will embed that content
into a full page with a root ``<html>`` and an embedded stylesheet.

In the future this feature will be moved to a separate frontend command
with more options.

The example listfile in the readme, for example, can be rendered as:

.. raw:: html
   :file: example_rendered.html
