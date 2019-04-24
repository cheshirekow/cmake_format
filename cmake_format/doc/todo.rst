====
TODO
====

* Allow option to infer keywords for commands which don't have a specification
* Add option to break long strings to make them fit
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
* Implement per-command algorithm order allowing to change the wrap preferences
  at a fine-grained level.
* Implement kwarg canonical ordering. Each kwarg parser has a canonical order
  associated with it. The formatter can re-order arguments when formatting to
  ensure that they are always written in the same order.
* Add a generic CMAKE_FORMAT_TAG token type matching ``# cmake-format: XXX``
  or ``# cmf: XXX`` strings.
* Implement an ``unpad_hashruler`` configuration option. If true, dont separate
  hashrulers from the leading comment character by a space.

cmake-lint
==========

* Create a cmake-lint program that checks for common errors like wrong
  variable names, wrong property names, etc.
* Annotate kwargs/args in parsers as optional, repeated, etc. Accumulate
  warnings/lint for violations.
* Types of  lint:

  * improper capitalization of statements, kwargs, or flags, keywords
  * optional kwargs not in canonical order
  * extra positional arguments

VS Code
=======

* Expand vscode extension to offer additional language support. See the
  following:

  * https://code.visualstudio.com/docs/extensionAPI/language-support
  * https://code.visualstudio.com/docs/extensions/example-language-server
  * https://microsoft.github.io/language-server-protocol/specification#textDocument_onTypeFormatting

* VScode language server protocol does not currently support semantic
  highlighting: https://github.com/Microsoft/language-server-protocol/issues/18
* But it can be implemented using custom messages to the language server such
  as https://github.com/cquery-project/cquery/issues/431
* An existing cmake extension is pretty good, but I think we can do better
  on code-completion and semantic highlighting

Sortabe Arguments
=================

* Don't treat tag comment specially with regard to trailing comment assignment,
  allow them to be attached to a preceeding parg or kwarg or whatever. This
  would allow::

    set(foobarbaz_ # cmake-format: sort
        bar
        baz
        foo
        zap
        zork)

  rather than forcing the comment on the second line

* Implement implicit sortable parts for add_executable and any other things
  that we know take a list of files.

Parser Refactor
===============

* Deal with the hack in parse_positionals working around
  ``install(RUNTIME COMPONENT runtime)``. The current solution is to only break
  if the subparser isn't expecting an exact number of tokens. The problem with
  this is that we will consume an RPAREN if a statement is malformed... and
  we probably shouldn't do that.
* Cleanup the HWRAP logic. Currently it's distributed in a number of places:

  * reflow() for everything but a StatementNode reduces it's linewidth by one
    in HPACK
  * PArgGroupNode._reflow() reduces the final linewidth by one if it's a
    _statement_terminal and we're in HWRAP mode
  * most nodes do the same work during HPACK and HWRAP
  * many nodes like StatementNode have old code that isn't needed now that
    ArgGroup exists

* Replace the rest of the legacy cmdspec tree with new style map of statement
  parse functions
* Add tests for all the different forms of ``install()`` and ``file()`` that
  we've implemented.
* Add a config option for users to specify custom commands using custom
  parse functions, rather than just the legacy dictionary specification.

Documentation
=============

* Remove all the config command line options from the README, as well as the
  example configuration. Move them into a separate documentation page.
* Don't embed the README in the official documentation. We could perhaps
  reuse snippets, possibly through some python scripting to generate the README
  page, but the README should probably contain a more compressed subset of the
  information on the documentation pages.
