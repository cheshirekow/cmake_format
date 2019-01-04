====
TODO
====

* Allow option to infer keywords for commands which don't have a specification
* Add option to break long strings to make them fit
* Create a cmake-highlight program to print the AST with markup, or export
  markup ranges for editors like vscode.
* Create a vscode extension. See the following:

  * https://code.visualstudio.com/docs/extensionAPI/language-support
  * https://code.visualstudio.com/docs/extensions/example-language-server
  * https://microsoft.github.io/language-server-protocol/specification#textDocument_onTypeFormatting

* VScode language server protocol does not currently support semantic
  highlighting: https://github.com/Microsoft/language-server-protocol/issues/18
* But it can be implemented using custom messages to the language server such
  as https://github.com/cquery-project/cquery/issues/431
* An existing cmake extension is pretty good, but I think we can do better
  on code-completion and semantic highlighting
* Create a cmake-lint program that checks for common errors like wrong
  variable names, wrong property names, etc.
* Use cmake --help-command --help-property --help-variable --help-module
  and parse the output to get the list of commands, properties, variable
  names, etc. This has been around since at least v2.8.8 so it's pretty
  available. It can definitely be used to filter available commands.
* Consider getting rid of config.endl and instead using
  ``io.open(newline='\n')`` or ``io.open(newline='\r\n')`` depending on config.
  Then just write ``\n`` and let the streamwriter translation take care of
  line endings.
* Make a distinction between argument comments and blocklevel or statement
  comments. Argument comments must be reflowed to (config.linewidth-1) if
  dangle_parens is false, while block level and statement comments may reflow
  up to (config.linewidth). Can probably just make this a flag in the
  CommentNode class rather than implementing a separate class for it. This
  can help to eliminate the need for, or at least simplify, the
  has_terminal_comment() hack.
* Deal with the case that the command name is so long or that the statement is
  nested so far that the open paren doesn't fit on the line and needs to be
  wrapped.
* Improve error messages for exceptions/assertions caused by malformed input.
* Implement a simple-wrap strategy, this might make sense for some file()
  commands
* Implement per-command algorithm order allowing to change the wrap preferences
  at a fine-grained level.

==============
Sort Arguments
==============

* Extend the command specification to include specification of different
  positional argument "groups". For instance in
  ``add_libarry(foo a.cc b.cc c.cc)``. There are four positional arguments but
  they are in two logical "groups". The first single-argument group ``foo`` is
  the name of the library. The second is the list of source files.
  In other words the specfication might look something like:
  ``add_library(<libname> [FLAGS] <source_files> [FLAGS])``
* Add to the cmdspec object a "sorted" flag. For any argument group that is
  configured to be "sorted", then sort the tokens between parsing and
  formatting. Probably add a ``formatter.sort_tree(parse_tree)`` in
  ``__main__.py`` immediately before ``formatter.layout_tree``.
* Add to the ``parser.TreeNode`` class a pointer to the cmdspec that was
  matched to that node during parsing. This will allow us to easily
  re-associate the cmdspec with the parse node when we are doing the sorting
  step.
* Implementation of the ``sort_tree`` then is to just walk the tree looking
  for any ``POSITIONAL_GROUP`` nodes which are associated with a ``cmdspec``
  for which ``sorted=True``. The child list of such a node is necessarily a
  list of tokens, so just sort the list on token spelling.
