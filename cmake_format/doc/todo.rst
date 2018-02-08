====
TODO
====

* Current treatment of statement arguments as a list is inappropriate for
  dealing with nested parenthesis. Instead, make arguments into subtrees so
  that a paren-enclosed unit is an argument, possibly with "sub-arguments"
  composed of the interior of the parens. Then format appropriately.
* Don't reflow all comment text. Sometimes you want text to be literal for
  things like::

    # --------------------------------
    # The stuff below this line os Foo
    # --------------------------------

