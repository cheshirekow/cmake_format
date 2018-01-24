====
TODO
====

* Current treatment of statement arguments as a list is inappropriate for
  dealing with nested parenthesis. Instad, make arguments into subtrees so
  that a paren-enclosed unit is an argument, possibly with "sub-arguments"
  composed of the interior of the parens. Then format appropriately.