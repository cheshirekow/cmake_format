====
TODO
====

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
  * local variable used but not assigned
  * local variable/global variable doesn't match regex
  * syntax hidden by variable expansion

VS Code
=======

* Expand vscode extension to offer additional language support. See the
  following:

  * https://code.visualstudio.com/docs/extensionAPI/language-support
  * https://code.visualstudio.com/docs/extensions/example-language-server
  * https://microsoft.github.io/language-server-protocol/specification#textDocument_onTypeFormatting

* Implement partial formatting (i.e. format highlight).
* VScode language server protocol does not currently support semantic
  highlighting: https://github.com/Microsoft/language-server-protocol/issues/18
* But it can be implemented using custom messages to the language server such
  as https://github.com/cquery-project/cquery/issues/431
* An existing cmake extension is pretty good, but I think we can do better
  on code-completion and semantic highlighting


Sortable Arguments
==================

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
* For add_library and add_executable, currently if the descriminator is a
  cmake variable it will get gobbled up
  with the positional arguments. They wont be sortable by default but they
  might be tagged sortable. In this case, break the pair of argument groups
  at the comment tag instead of after library/executable name.

Current Issues
==============

* Need some kind of fallback for commands like `file()` when the descriminator
  argument is a variable dereference. For instance `file(${descr})`. What
  should we do in that case? Should we infer based on remaining arguments,
  fallback to a standard parser with a large set of kwargs and flags?

Cost Function
=============

Implement something better than :code:`max-subgroups-hwrap` and
:code:`layout-passes`.
Probably both of these can be rolled up into a some kind of cost function
that accounts for both issues. For instance, a cost function which
penalizes number of lines, number of arguments on a line, and indentation
would generally perfer a single line, would perhaps allow HWRAP but only
if it was at most two lines, would allow VPACK but only if the statment
name is not too long.

Release Process
===============

Add cmake rules for ``prep-release`` and ``test-release`` that will
automatically create a release commit and double check certain things:

1. Closed issues in changelog are also closed in the commit message
2. Version number is not ``dev``
3. Version number is incremented
4. Execute the screw-users test

Parse Stack Refactor
====================

There are a couple of things that are a bit clunky about the current
implementation of the parser stack context. Currently we only have the
:code:`breakstack` in each parse function. I think we want some more context.
One thing that we should probably add is the stack of parse nodes that have
been opened up to the current context. The initiating token for each parse
node can be used to infer some properties of tokens as we process them.

* Github issue #122: ambiguity in the nesting level of a line comment which
  might belong to the end of a nested argument list, or might belong to the
  parent argument list.
* Look-ahead at the next semantic token when deciding whether or not to
  break out of the current scope. Otherwise comments will get globbed up in
  the nested scope when they were originally written in outer scope.
* If the look-ahead indicates that the next semantic token would break us
  up the stack, then any comment between "here" and that token belongs to
  the child set of one of the nodes somewhere in that stack region. One way
  of associating it consistently is to find the latest parse node that starts
  no later than the current comment node.
* Deal with the hack in parse_positionals working around
  ``install(RUNTIME COMPONENT runtime)``. The current solution is to only break
  if the subparser isn't expecting an exact number of tokens. The problem with
  this is that we will consume an RPAREN if a statement is malformed... and
  we probably shouldn't do that.


After Refactor
==============

01. Move as many tests as possible into :code:`.cmake` sidecar files.

02. Split :code:`formatter.py` into :code:`format_tree.py` and
    :code:`formatter.py`

03. Implement :code:`wrap` tags. I'm not sure what the tag string should
    be, maybe :code:`wrap`, :code:`list`, :code:`vertical/nest`, but whatever
    it is, it should record within the parse node a forced wrap decition and
    override the trial/error logic. That way an empty comment can be used to
    force a line-wrap, but a specific comment can be used to force a more
    specific decision.
04. There are still many more cmake functions that need parser mappings.

    * :code:`list()`
    * :code:`target_compile_definitions()`

05. Make a test that executes cmake to get the
    list of function names and make sure they're all in the database.
06. Replace the rest of the legacy cmdspec tree with new style map of statement
    parse functions
07. Add tests for all the different forms of ``install()`` and ``file()`` that
    we've implemented.
08. Add a config option for users to specify custom commands using custom
    parse functions, rather than just the legacy dictionary specification.
09. Add option to infer keywords for commands which don't have a specification
10. Add option to break long strings to make them fit
11. Use cmake --help-command --help-property --help-variable --help-module
    and parse the output to get the list of commands, properties, variable
    names, etc. This has been around since at least v2.8.8 so it's pretty
    available. It can definitely be used to filter available commands.
12. Consider getting rid of config.endl and instead using
    ``io.open(newline='\n')`` or ``io.open(newline='\r\n')`` depending on
    config. Then just write ``\n`` and let the streamwriter translation take
    care of line endings.
13. Deal with the case that the command name is so long or that the statement
    is nested so far that the open paren doesn't fit on the line and needs to
    be wrapped.
14. Improve error messages for exceptions/assertions caused by malformed input.
15. Implement kwarg canonical ordering. Each kwarg parser has a canonical order
    associated with it. The formatter can re-order arguments when formatting to
    ensure that they are always written in the same order.
16. Add a generic CMAKE_FORMAT_TAG token type matching ``# cmake-format: XXX``
    or ``# cmf: XXX`` strings and don't necessarily treat them like comments.
17. Implement an ``unpad_hashruler`` configuration option. If true, dont
    separate hashrulers from the leading comment character by a space.
18. Enable an option to parse sentinel comments `#< comment here` as argument
    comments (instead of relying on existing columnization to merge
    multiple argument comment lines).
19. Deduplicate code in in :code:`consume_comment` and
    :code:`consume_trailing_comment` which are pretty much the same now.
20. Figure out what to do the :code:`needs_wrap=True` logic in
    :code:`ArgGroupNode._reflow` if an argument wraps internally. In some cases
    it looks bad, but in some cases it looks good. See case studies for
    internally wrapped positionals.
21. The _statement_terminal hack is insufficient for dealing with parengroups.
    We need some other mechanism to deal with multiple closing parentheses.
    Probably we need to pass down some kind of :code:`StackContext` including
    a member of :code:`n_open_parens`.
22. Deduplicate the common reflow logic of :code:`StatementNode` and
    :code:`KwargGroupNode` (both of which nest). Also potentially the reflow
    logic of :code:`ArgGroupNode` and :code:`PargGroupNode` (both of which
    verticalize).
23. Rename :code:`ParseNode.node_type` to :code:`ParseNode.type`
24. There are a couple more TODO's in :code:`formatter.py`
25. Currently it's rather challenging to know in the formatter whether or not
    a particular comment would be re-parsed as an argument comment if we were
    to move it. This tag/mark might be moot if we just allow special comments
    to be argument comments (which would allow them to be attached to a
    particular argument). See the logic in PargGroupNode :code:`_reflow()`
    where a comment is matched.
26. :code:`max_prefix_chars` isn't exactly the right thing to switch on. What
    we really want is something that depends on the current indentation level.
    I think what we really want is :code:`min_suffix_chars`, or, rather, given
    a :code:`prefix_length` and a current indentation, look at how many chars
    are available for content. If that number is too small, then force nesting.
    Think about this more and look at some cases based on a selection of
    statement names and keywords. Maybe compute some statistics on these and
    use that to inform the selection.
27. Implement columnization, (successive kwarg children share are vertically
    aligned, share a column).
28. Implement per-command :code:`layout_passes`
29. Add :code:`include` config option, allowing to refer to an external
    configuration file.

