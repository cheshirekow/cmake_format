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
  only has effect at the current tree level (and those below). This will allow
  a number of new features.

  1. It will make it much easier to implement additional formatting strategies
     at each level
  2. It will allow activation/deactivation/reorder of strategy preferences
  3. It will allow us to deal with outer parentheses easier

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
  and parse the output to get the list of commands, properties, varaiable
  names, etc. This has been around since at least v2.8.8 so it's pretty
  available. It can definitely be used to filter available commands.
* Clean newlines and trailing whitespace from block comments or block
  variables
* Make lineending (windows/unix) an option
* Consider getting rid of config.endl and instead using
  ``io.open(newline='\n')`` or ``io.open(newline='\r\n')`` depending on config.
  Then just write ``\n`` and let the streamwriter translation take care of
  line endings.
* Add --line-ending=auto option
