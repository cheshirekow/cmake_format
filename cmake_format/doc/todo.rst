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
