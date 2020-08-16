============
Linter notes
============

.. default-role:: literal
.. highlight:: none

---------------------------
Variable naming conventions
---------------------------

The default patterns used for variable naming convention is chosen to match
the dominant convention of the listfiles distributed with cmake itself. The
tool `analyze_naming.py` was used to classify each variable assignment in
all modules from cmake `3.10` yielding the following counts::

  PARENT
  ======
  other: 237
  '[A-Z][A-Z0-9_]+' 335
  '[a-z][a-z0-9_]+' 146
  '_[A-Z0-9_]+' 62
  '_[a-z0-9_]+' 236

  LOCAL
  =====
  other: 375
  '[A-Z][A-Z0-9_]+' 646
  '[a-z][a-z0-9_]+' 1220
  '_[A-Z0-9_]+' 375
  '_[a-z0-9_]+' 450

  DIRECTORY
  =========
  other: 235
  '[A-Z][A-Z0-9_]+' 2140
  '[a-z][a-z0-9_]+' 111
  '_[A-Z0-9_]+' 515
  '_[a-z0-9_]+' 182

  LOOP
  ====
  other: 72
  '[A-Z][A-Z0-9_]+' 98
  '[a-z][a-z0-9_]+' 288
  '_[A-Z0-9_]+' 79
  '_[a-z0-9_]+' 114

  ARGUMENT
  ========
  other: 17
  '[A-Z][A-Z0-9_]+' 159
  '[a-z][a-z0-9_]+' 512
  '_[A-Z0-9_]+' 60
  '_[a-z0-9_]+' 184


