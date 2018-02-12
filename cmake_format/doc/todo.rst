====
TODO
====

* Current treatment of statement arguments as a list is inappropriate for
  dealing with nested parenthesis. Instead, make arguments into subtrees so
  that a paren-enclosed unit is an argument, possibly with "sub-arguments"
  composed of the interior of the parens. Then format appropriately.
* It's also inappropriate for some kwargs that take kwargs themselves. For
  instance ``set_target_properties()`` has the ``PROPERTIES`` kwargs which
  takes both a property name and property value. It would be better to nest
  the formatting of these arguments.
* Ideas for new comment reflow policy:

  *  Only reflow a paragraph if it contains any lines longer than the current
     line width.
  *  Parse comments as restructured text or markdown, then write them out in
     formatted way.
  *  Only allow structured textr comments at the block level. Always reflow
     comments that are part of a statement or immediately following a statement.
  *  If a paragraph stars with punctuation then don't reflow it. Otherwise
     reflow it.

* Don't make format-on and format-off last beyond the current scope level.
* Refactor formatter to work entirely at a tree level. Formatter active/inactive
  only has effect at the current tree level (and those below).
