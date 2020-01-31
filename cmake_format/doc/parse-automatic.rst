=================
Automatic Parsers
=================

cmake provides help commands which can print out the usage information for all
of the builtin statements that it supports. You can get a list of commands
with

.. code::

   cmake --help-command-list

And you can get the help text for a command with (for example):

.. code::

   cmake --help-command add_custom_command

In general (but not always) the usage string is given an a restructured-text
block that looks like this:

.. code::

    ::

     add_custom_command(TARGET <target>
                        PRE_BUILD | PRE_LINK | POST_BUILD
                        COMMAND command1 [ARGS] [args1...]
                        [COMMAND command2 [ARGS] [args2...] ...]
                        [BYPRODUCTS [files...]]
                        [WORKING_DIRECTORY dir]
                        [COMMENT comment]
                        [VERBATIM] [USES_TERMINAL])

The syntax of these usage strings isn't 100% consistent but if we could
generate a parser that even understands *most* of these strings then that
would greatly reduce the maintenance load.


--------------
Expect Objects
--------------

The output of the specification parser is an "Expect Tree". A tree of
objects representing what is expected from a statement. If a sequence
of tokens satisfies an expected subtree then the a corresponding parse
tree is generated. If a mandatory expected subtree is not satisfied
then an error is generated. If an optional expected subtree is not
satisfied then the next sibling is tried.


------------
Case studies
------------


Inconsistent usage of angle brackets
====================================

Sometimes mandatory arguments are shown in angle brackets, sometimes not. I
can't really figure a pattern for when they are used and when  they are not.


Ellipses
========

Whether or not there is a space between an elipsis and the preceeding token
seems to imply something about what is repeated.

::

 add_custom_command(TARGET <target>
                    PRE_BUILD | PRE_LINK | POST_BUILD
                    COMMAND command1 [ARGS] [args1...]
                    [COMMAND command2 [ARGS] [args2...] ...]
                    [BYPRODUCTS [files...]]
                    [WORKING_DIRECTORY dir]
                    [COMMENT comment]
                    [VERBATIM] [USES_TERMINAL])


Note that the elipsis for "COMMAND" is inside the bracket above, but is
outside the bracket here:

::

 add_dependencies(<target> [<target-dependency>]...)


Choices
=======

Pipe character is used to separate choices.

::

 configure_file(<input> <output>
                [COPYONLY] [ESCAPE_QUOTES] [@ONLY]
                [NEWLINE_STYLE [UNIX|DOS|WIN32|LF|CRLF] ])

Sometimes it's a mandatory choice

::

 ctest_test([BUILD <build-dir>] [APPEND]
            [START <start-number>]
            [END <end-number>]
            [STRIDE <stride-number>]
            [EXCLUDE <exclude-regex>]
            [INCLUDE <include-regex>]
            [EXCLUDE_LABEL <label-exclude-regex>]
            [INCLUDE_LABEL <label-include-regex>]
            [EXCLUDE_FIXTURE <regex>]
            [EXCLUDE_FIXTURE_SETUP <regex>]
            [EXCLUDE_FIXTURE_CLEANUP <regex>]
            [PARALLEL_LEVEL <level>]
            [TEST_LOAD <threshold>]
            [SCHEDULE_RANDOM <ON|OFF>]
            [STOP_TIME <time-of-day>]
            [RETURN_VALUE <result-var>]
            [CAPTURE_CMAKE_ERROR <result-var>]
            [QUIET]
            )

Sometimes the choice is among literals, in which case there are no surrounding
brackets.

::

 file(GLOB <variable>
      [LIST_DIRECTORIES true|false] [RELATIVE <path>]
      [<globbing-expressions>...])


Manditory Sequence
==================

In this case the literal pattern is listed inside the mandatory group pattern
(angle brackets).

::

 file(GENERATE OUTPUT output-file
      <INPUT input-file|CONTENT content>
      [CONDITION expression])

This one is pretty complex, and also demonstrates the nested bracket usage.
I think the indication here is that "you must have one of these choices.

::

 get_property(<variable>
              <GLOBAL             |
               DIRECTORY [dir]    |
               TARGET    <target> |
               SOURCE    <source> |
               INSTALL   <file>   |
               TEST      <test>   |
               CACHE     <entry>  |
               VARIABLE>
              PROPERTY <name>
              [SET | DEFINED | BRIEF_DOCS | FULL_DOCS])

Nested Optionals
================

::

 install(TARGETS targets... [EXPORT <export-name>]
         [[ARCHIVE|LIBRARY|RUNTIME|OBJECTS|FRAMEWORK|BUNDLE|
           PRIVATE_HEADER|PUBLIC_HEADER|RESOURCE]
          [DESTINATION <dir>]
          [PERMISSIONS permissions...]
          [CONFIGURATIONS [Debug|Release|...]]
          [COMPONENT <component>]
          [OPTIONAL] [EXCLUDE_FROM_ALL]
          [NAMELINK_ONLY|NAMELINK_SKIP]
         ] [...]
         [INCLUDES DESTINATION [<dir> ...]]
         )


Multiple Forms
==============

::

 string(SUBSTRING <string> <begin> <length> <output variable>)
 string(STRIP <string> <output variable>)
 string(GENEX_STRIP <input string> <output variable>)
 string(COMPARE LESS <string1> <string2> <output variable>)


----------
Conclusion
----------

After implementing a prototype parser and testing it on some of the above cases
it is clear that the help text is not very consistent and is likely to be very
challenging to get an implementation that works reliabily and knows when it
fails. For example:

::

 add_custom_command(TARGET <target>
                    PRE_BUILD | PRE_LINK | POST_BUILD
                    COMMAND command1 [ARGS] [args1...]
                    [COMMAND command2 [ARGS] [args2...] ...]
                    [BYPRODUCTS [files...]]
                    [WORKING_DIRECTORY dir]
                    [COMMENT comment]
                    [VERBATIM] [USES_TERMINAL])

In this form of the command, the `PRE_BUILD` `PRE_LINK` or `POST_BUILD`
argument is required. Normally it seems like they would put this in angle
brackets as `<PRE_BUILD|PRE_LINK|POST_BUILD>` but they do not. So it's
ambiguous where the pipes are splitting and what the groups are.
