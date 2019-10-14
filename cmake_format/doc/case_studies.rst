============
Case Studies
============

This is a collection of interesting cases that are illustrative of different
concepts for formatting options.

--------------------
Positional Arguments
--------------------

Lots of short args, looks good all on one line::

    add_subdirectories(foo bar baz foo2 bar2 baz2)


Also doesn't look too bad when wrapped horizontally::

    add_subdirectories(
        foo bar baz foo2 bar2 baz2 foo3 bar3 baz3 foo4 bar4 baz4 foo5 bar5 baz5
        foo6 bar6 baz6 foo7 bar7 baz7 foo8 bar8 baz8 foo9 bar9 baz9)

Though probably matches expectations better if it is wrapped vertically,
even if it does look like shit::

    add_subdirectories(
        foo
        bar
        baz
        foo2
        bar2
        baz2
        foo3
        bar3
        baz3
        foo4
        bar4
        baz4
        foo5
        bar5
        baz5
        foo6
        bar6
        baz6
        foo7
        bar7
        baz7
        foo8
        bar8
        baz8
        foo9
        bar9
        baz9)

Just a couple of long args, looks bad wrapped horizontally::

    set(HEADERS very_long_header_name_a.h very_long_header_name_b.h
        very_long_header_name_c.h)

and looks better wrapped vertically, horizontally nested::

    set(HEADERS
        very_long_header_name_a.h
        very_long_header_name_b.h
        very_long_header_name_c.h)

also looks pretty good packed after the first argument::

    set(HEADERS very_long_header_name_a.h
                very_long_header_name_b.h
                very_long_header_name_c.h)

or possibly nested::

    set(HEADERS
          very_long_header_name_a.h
          very_long_header_name_b.h
          very_long_header_name_c.h)

    set(
      HEADERS
        very_long_header_name_a.h
        very_long_header_name_b.h
        very_long_header_name_c.h)

 but this starts to look a little inconsistent when other arguments are
 used::

    set(
      HEADERS PARENT_SCOPE
        very_long_header_name_a.h
        very_long_header_name_b.h
        very_long_header_name_c.h)

Lots of medium-length args, looks good vertical, horizontally nested::

    set(SOURCES
        source_a.cc
        source_b.cc
        source_d.cc
        source_e.cc
        source_f.cc
        source_g.cc)

Interestingly, if the PARGGROUP list is one level deeper, the distinction
between what looks good is a little blurrier. With lots of short names,
I think it looks good both ways::

    # This very long command should be broken up along keyword arguments
    foo(nonkwarg_a nonkwarg_b
        HEADERS a.h b.h c.h d.h e.h f.h
        SOURCES a.cc b.cc d.cc
        DEPENDS foo
        bar baz)

versus::

    # This very long command should be broken up along keyword arguments
    foo(nonkwarg_a nonkwarg_b
        HEADERS a.h
                b.h
                c.h
                d.h
                e.h
                f.h
        SOURCES a.cc b.cc d.cc
        DEPENDS foo
        bar baz)

though it does seems like the same rules can be applied here if we include
some configuration for both number of arguments and length of arguments.

-----------------
Keyword Arguments
-----------------

When chidren include both positionals and keyword arguments,
it looks good with each group wrapped vertically, while grand children
are wrapped horizontally::

    set_target_properties(
      foo bar baz
      PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")

I think it makes sense even with just a single positional, even if it is a
little sparsish::

    set_target_properties(
      foo
      PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra -Wfoobarbazoption")

Another option is to put the "short" positional arguments on the first line,
but while this might look good in some cases I think the cost of inconstency
is high. This also introduces some readability issues in that the
positional arguments are easy to overlook in this layout::

    set_target_properties(foo
      PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra -Wfoobarbazoption")

Though in the case that it could all be on one line so we should do that::

    set_target_properties(
        foo PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")

And ``set_target_properties`` is actually kind of special because
``PROPERITES`` doesn't act much like a keyword. It's more of a separator after
which we parse thins in pairs. This might look nicer, but I'm not sure we can
really make it fit with other rules::

    set_target_properties(
      foo PROPERTIES
      COMPILE_FLAGS "-std=c++11 -Wall -Wextra -Wfoobarbazoption"
      LINKER_FLAGS "-fpic -someotheroption")

Though with custom parse logic we might be able to do so. The custom parser
would include ``PROPERTIES`` in the positional arguments and would label the
first half of each pair as a ``KEYWORD`` node.

-----
set()
-----

``set()`` is somewhat of a special case due to things like this::

    set(args
        OUTPUT fizz.txt
        COMMAND foo --bar --baz
        DEPENDS foo.txt bar.txt baz.txt
        COMMENT "This is my rule"
        BYPRODUCTS buzz.txt)
    add_custom_command(${arg})

I suppose it's not the worse case that we just horizontally wrap it by default
in which case the user can enforce wrapping with line comments. It would be
nice if they could somehow annotate it though, like with a comment
``# cmf: as=add_custom_command``. That sounds complicated though. One really
fancy solution would be to scan for potential kwargs, then try to match against
a known command based on the registry.

Note that ``set()`` isn't the only command like this. There are likely to be
other commands, specifically wrapper commands, that might take an unstructured
argument list which becomes structured under the hood.

.. _comments-case-study:

--------
Comments
--------

Argument comments can get a little tricky, because this looks bad::

    set(HEADERS header_a.h header_b.h header_c.h header_d.h # This comment is
                                                            # pretty long and
                                                            # if it's argument
                                                            # is close to the
                                                            # edge of the column
                                                            # then the comment
                                                            # gets wrapped very
                                                            # poorly
        header_e.h header_f.h)

and this looks good::

    set(HEADERS
        header_a.h
        header_b.h
        header_c.h
        header_d.h # This comment is pretty long and if it's argument is close
                   # to the edge of the column then the comment gets wrapped
                   # very poorly
        header_e.h
        header_f.h)

but this also looks acceptable and I could imagine some organization choosing
to go this route with their style configuration::

    set(HEADERS header_a.h header_b.h header_c.h
        header_d.h # This comment is pretty long and if it's argument is close
                   # to the edge of the column then the comment gets wrapped
                   # very poorly
        header_e.h header_f.h)

So I'm not sure that the presence of a line comment should necessarily
predicate a vertical wrapping. Rather, I think the choice of wrapping strategy
should be independant of the presence of a comment. In the case of horizontal
wrapping though, we need some kind of threshold or score to determine when
a comment has gotten "too smooshed" and the whole thing should move to the
next line. In the example above::

    # option A:                                             ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
    set(HEADERS header_a.h header_b.h header_c.h header_d.h ▏# This comment is   ▕
                                                            ▏# pretty long and   ▕
                                                            ▏# if it's argument  ▕
                                                            ▏# is close to the   ▕
                                                            ▏# edge of the column▕
                                                            ▏# then the comment  ▕
                                                            ▏# gets wrapped very ▕
                                                            ▏# poorly            ▕
        header_e.h header_f.h)                              ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

    # option B:
    set(HEADERS header_a.h header_b.h header_c.h▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        header_d.h ▏# This comment is pretty long and if it's argument is close▕
                   ▏# to the edge of the column then the comment gets wrapped  ▕
                   ▏# very poorly                                              ▕
        header_e.h header_f.h)▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

"Option A" lays out the comment on eight lines while "option B" lays out the
comment in three lines. I'm not sure what the threshold should be for choosing
one over the other. Should it be based on how many lines the comment is, or
how much whitespace we introduce due to it? In "Option A" we introduce seven
lines of whitespace between consecutive rows of arguments whereas in "Option B"
we only add two. Should it be based on aspect ratio?

And, honestly, "Option A" isn't all that bad. I'm not sure it would cross
everyones threshold for inducing a wrap.

For this particular example I think the best looking layout is the vertical
wrapping, but we don't want the presence of a line comment to automatically
indluce vertical wrapping. For instance in this example, we definitely want
to keep horizontal wrapping, we just want the line comment to induce an early
wrap::

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      COMMAND sphinx-build -M html #
              ${CMAKE_CURRENT_SOURCE_DIR} #
              ${CMAKE_CURRENT_BINARY_DIR}
      COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      DEPENDS ${foobar_docs}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

One comprimise solution is to change the behavior of the line comment
depending on the nature of the PARGGROUP. The parser can tag each PARGGROUP
with it's ``default_wrap`` (either "horizontal" or "vertical"). Then,
when a wrap is required the default wrap can be used. A wrap might be required
due to:

* arguments overflow the column width
* exceed threshold in number or size of arguments
* presence of a line comment

This comprimise is the reason the previous version of ``cmake-format`` had a
distinct ``HPACK`` wrapping algorithm. It allowed us a configuration where
all wrapping would be vertical wrapping.

A second comprimise solution, which is compatible with the previous solution,
is to make the wrapping tunable by an annotation comment. For instance::

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      COMMAND sphinx-build -M html # cmf:hwrap
              ${CMAKE_CURRENT_SOURCE_DIR} #
              ${CMAKE_CURRENT_BINARY_DIR}
      COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      DEPENDS ${foobar_docs}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

where the ``hwrap`` annotation would change the default behavior of the
line comment from inducing vertical wrapping to inducing a newline within
vertical wrapping. If the annotation syntax requires too many characters, we
could use something like double-hash ``##``, hash-h ``#h`, or hash-v (``#v``)
for this purpose. This could be a sandard "microtag" format including the
ability to set the list sortable. For example: ``#v,s`` would be
"vertical, sortable"

Another interesting case is if we have an argument comment on a keyword
argument, or a prefix group. For example::

    set(foobarbaz # comment about foobarbaz
        value_one value_two value_three value_four value_five value_six
        value_seven value_eight)

Should that be formatted as above, or as::

    set(foobarbaz # comment about foobarbaz
                  value_one value_two value_three value_four value_five
                  value_six value_seven value_eight)

If we're already formatting set as::

    set(foobarbaz value_one value_two value_three value_four value_five
                  value_six value_seven value_eight)

-------
Nesting
-------

When logic get's nested, the need to nest after long command names becomes
more apparent::

    if(foo)
      if(sbar)
        # This comment is in-scope.
        add_library(
          foo_bar_baz
          foo.cc
          bar.cc # this is a comment for arg2 this is more comment for
                 # arg2, it should be joined with the first.
          baz.cc) # This comment is part of add_library

        other_command(
            some_long_argument some_long_argument) # this comment is very
                                                   # long and gets split
                                                   # across some lines

        other_command(some_long_argument some_long_argument some_long_argument)
        # this comment is even longer and wouldn't make sense to pack at the
        # end of the command so it gets it's own lines
        endif()
      endif()

Another good example is ``add_custom_comand()``::

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
              ${CMAKE_CURRENT_BINARY_DIR}
      COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/foobar_doc.stamp
      DEPENDS ${foobar_docs}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

But note the tricky bit here. I think we definitely want the COMMAND
ARGGOUP (which is a single PARGGROUP) to be horizontally wrapped.

.. _install-case-study:

There are also some commands with second (or more) levels of keyword
arguments, and it's not clear if the nesting rules are best applied
top-down::

  install(
    TARGETS foo bar baz
    ARCHIVE DESTINATION <dir>
            PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
            CONFIGURATIONS Debug Release
            COMPONENT foo-component
            OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP
    LIBRARY DESTINATION <dir>
            PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
            CONFIGURATIONS Debug Release
            COMPONENT foo-component
            OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP
    RUNTIME DESTINATION <dir>
            PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
            CONFIGURATIONS Debug Release
            COMPONENT foo-component
            OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP)

Or bottom-up::

  install(
    TARGETS foo bar baz
    ARCHIVE
      DESTINATION <dir>
      PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
      CONFIGURATIONS Debug Release
      COMPONENT foo-component
      OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP
    LIBRARY
      DESTINATION <dir>
      PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
      CONFIGURATIONS Debug Release
      COMPONENT foo-component
      OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP
    RUNTIME
      DESTINATION <dir>
      PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
      CONFIGURATIONS Debug Release
      COMPONENT foo-component
      OPTIONAL EXCLUDE_FROM_ALL NAMELINK_SKIP)

.. _conditionals-case-study:

------------
Conditionals
------------

Treating boolean operators as keyword arguments works pretty well, so long
as we treat parenthetical groups as a single unit::

    set(matchme "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
    if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
       OR (CONFIG_AV1_ENCODER
           AND CONFIG_ENCODE_PERF_TESTS
           AND "${var}" MATCHES "_ENCODE_PERF_TEST_")
       OR (CONFIG_AV1_DECODER
           AND CONFIG_DECODE_PERF_TESTS
           AND "${var}" MATCHES "_DECODE_PERF_TEST_")
       OR (CONFIG_AV1_ENCODER AND "${var}" MATCHES "_TEST_ENCODER_")
       OR (CONFIG_AV1_DECODER AND "${var}" MATCHES "_TEST_DECODER_"))
      list(APPEND aom_test_source_vars ${var})
    endif()

I don't think there's any reason to add structure for the internal operators
like ``MATCHES``. In particular children of a boolean operator can be simple
positional argument groups (horizontally-wrapped). We can tag the internal
operator as a keyword but we don't need to create a KWARGGROUP for it.

------------------------------
Internally Wrapped Positionals
------------------------------

The third kwarg (AND) in this statement looks bad because it is Internally
wrapped. The second option looks better:

.. code:: cmake

    set(matchme "_DATA_\|_CMAKE_\|INTRA_PRED\|_COMPILED\|_HOSTING\|_PERF_\|CODER_")
    if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
       OR (CONFIG_AV1_ENCODER AND CONFIG_ENCODE_PERF_TESTS AND "${var}" MATCHES
                                                               "_ENCODE_PERF_TEST_"
          ))
      list(APPEND aom_test_source_vars ${var})
    endif()

    set(matchme "_DATA_\|_CMAKE_\|INTRA_PRED\|_COMPILED\|_HOSTING\|_PERF_\|CODER_")
    if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
       OR (CONFIG_AV1_ENCODER
           AND CONFIG_ENCODE_PERF_TESTS
           AND "${var}" MATCHES "_ENCODE_PERF_TEST_"))
      list(APPEND aom_test_source_vars ${var})
    endif()

However, this short :code:`set()` statement looks better if we don't push the
internally wrapped argument to the next line:

.. code:: cmake

    set(sources # cmake-format: sortable
                bar.cc baz.cc foo.cc)

Perhaps the difference is that in the latter case it's going to consume two
lines anyway... whereas in the former case it would only consume one
line.

--------------------
Columnized arguments
--------------------

Some very long statements with a large number of keywords might look nice
and organized if we columize the child argument groups. For example:

.. code:: cmake

    ExternalProject_Add(
        FOO
        PREFIX           ${FOO_PREFIX}
        TMP_DIR          ${TMP_DIR}
        STAMP_DIR        ${FOO_PREFIX}/stamp
        # Download
        DOWNLOAD_DIR     ${DOWNLOAD_DIR}
        DOWNLOAD_NAME    ${FOO_ARCHIVE_FILE_NAME}
        URL              ${STORAGE_URL}/${FOO_ARCHIVE_FILE_NAME}
        URL_MD5          ${FOO_MD5}
        # Patch
        PATCH_COMMAND    ${PATCH_COMMAND} ${PROJECT_SOURCE_DIR}/patch.diff
        # Configure
        SOURCE_DIR       ${SRC_DIR}
        CMAKE_ARGS       ${CMAKE_OPTS}
        # Build
        BUILD_IN_SOURCE  1
        BUILD_BYPRODUCTS ${CUR_COMPONENT_ARTIFACTS}
        # Logging
        LOG_CONFIGURE    1
        LOG_BUILD        1
        LOG_INSTALL      1
    )

Note what :code:`clang-format` does for these cases. If two consecutive
keywords are more than :code:`n` characters different in length, then break
columns, which might come out something like this:

.. code:: cmake

    ExternalProject_Add(
        FOO
        PREFIX    ${FOO_PREFIX}
        TMP_DIR   ${TMP_DIR}
        STAMP_DIR ${FOO_PREFIX}/stamp
        # Download
        DOWNLOAD_DIR  ${DOWNLOAD_DIR}
        DOWNLOAD_NAME ${FOO_ARCHIVE_FILE_NAME}
        URL     ${STORAGE_URL}/${FOO_ARCHIVE_FILE_NAME}
        URL_MD5 ${FOO_MD5}
        # Patch
        PATCH_COMMAND ${PATCH_COMMAND} ${PROJECT_SOURCE_DIR}/patch.diff
        # Configure
        SOURCE_DIR ${SRC_DIR}
        CMAKE_ARGS ${CMAKE_OPTS}
        # Build
        BUILD_IN_SOURCE  1
        BUILD_BYPRODUCTS ${CUR_COMPONENT_ARTIFACTS}
        # Logging
        LOG_CONFIGURE 1
        LOG_BUILD     1
        LOG_INSTALL   1
    )

As an experimental feature, we could require a tag :code:`# cmf: columnize`
to enable this formatting.

-------------------------
Algorithm Ideas and Notes
-------------------------

Layout Passes
=============

Up through version 0.5.2 each node would lay itself out using pass numbers
``[0, <parent-passno>]``. This worked pretty well, but actually I would like
the nesting to be a little more depth dependant. For example I would like
depth 0 (statement) to nest rather early, while I would like higher depths
(i.e. KWARGS) to nest later, but go vertical earlier.

One alternative is to have a global ``passno`` and apply different rules at
each pass until things fit, but the probem with this option is that two
subtrees might require fastly different passes. We don't want to
vertically wrap one all kwargs just because one needs to.
