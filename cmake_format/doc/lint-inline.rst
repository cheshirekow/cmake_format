=================
Inline Directives
=================

`cmake-lint` supports inline directives to help control local behavior. The
format of these directives is a cmake line comment with the following
format:

.. code::

  # cmake-lint: <body>

-------
Pragmas
-------

disable
=======

You may specify a list of error codes to locally disable. You may specify
a comma separate list of codes to disable:

.. code::

  # cmake-lint: disable=<code1>,<code2>,<code3>,...

Example:

.. code::

  # cmake-lint: disable=C0103
  foreach(LOOPVAR2 a b c d)
    # pass
  endforeach()

.. warning::

  Currently this pragma must be specified at body scope (e.g. it cannot be a
  comment within a statement) and it applies for the duration of the scope.
  This behavior will likely change in the future.
