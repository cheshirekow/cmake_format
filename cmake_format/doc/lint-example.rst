=======
Example
=======

Given the following linty file:

.. dynamic: lint-in-begin

.. code:: cmake

    # The line is too long and exceeds the default 80 character column limit enforced cmake-lint

    # This line has trailing whitespace

    # This line has the wrong line endings


    function(BAD_FUNCTION_NAME badArgName good_arg_name)
      # Function names should be lower case
    endfunction()

    #
    macro(bad_macro_name badArgName good_arg_name)
      # Macro names should be upper case
    endmacro()

    if(FOOBAR)
      foreach(loopvar a b c d)
        # cmake-lint: disable=C0103
        foreach(LOOPVAR2 a b c d)
          # pass
        endforeach()
      endforeach()
      foreach(LOOPVAR3 a b c d)
        # pass
      endforeach()

    endif()

    set(VARNAME varvalue CACHE STRING)

    cmake_minimum_required_version(VERSION 2.8.11 VERSION 3.16)

    add_custom_command()

    set(_form TARGET PRE_BUILD)
    add_custom_command(
      ${form}
      COMMAND echo "hello"
      COMMENT "echo hello")

    add_custom_command(
      TARGRET PRE_BUILD
      COMMAND echo "hello"
      COMMENT "echo hello")

    add_custom_command(OUTPUT foo)

    add_custom_target(foo ALL)

    file()

    set(_form TOUCH)
    file(${form} foo.py)

    file(TOUCHE foo.py)

    break()

    continue()

    # foo: docstring
    function(foo)
      foreach(arg ${ARGN})
        if(arg STREQUAL "FOO")
          # parse FOO
        elseif(arg STREQUAL "BAR")
          # parse BAR
        elseif(arg MATCHES "BAZ.*")
          # parse BAZ
        endif()
      endforeach()
    endfunction()

    set(_foo "hello") set(_bar "goodbye")

    set(_foo "hello")


    set(_bar "goodbye")

    # foo: docstring
    function(foo "arg-name")
      # pass
    endfunction()

    # foo: docstring
    function(foo arg arg)
      # pass
    endfunction()

    # foo: docstring
    function(foo arg ARG)
      # pass
    endfunction()

    return()
    message("This code is unreachable")

    # cmake-lint: disable=E0109,C0321
    # foo:docstring, too many arguments
    function(foo, a0, a1, a2, a3, a4, a5)

      # Too many branches, too many returns
      if(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      elseif(blah) return()
      else() return()
      endif()

      # too many statements
      message(foo) message(foo) message(foo) message(foo) message(foo) message(foo)
      message(foo) message(foo) message(foo) message(foo) message(foo) message(foo)
      message(foo) message(foo) message(foo) message(foo) message(foo) message(foo)
      message(foo) message(foo) message(foo) message(foo) message(foo) message(foo)
      message(foo) message(foo) message(foo) message(foo) message(foo) message(foo)
    endfunction()

    # cmake-lint: disable=C0111
    # cache (global) variables should be upper snake
    set(MyGlobalVar CACHE STRING "my var")
    # internal variables are treated as private and should be upper snake with an
    # underscore prefix
    set(MY_INTERNAL_VAR CACHE INTERNAL "my var")
    # directory-scope variables should be upper-snake (public) or lower-snake with
    # underscore prefix
    set(_INVALID_PRIVATE_NAME "foo")
    set(invalid_public_name "foo")
    function(foo)
      set(INVALID_LOCAL_NAME "foo")
    endfunction()

    # This file is missing a final newline
.. dynamic: lint-in-end

The output is:

.. dynamic: lint-out-begin

.. code:: text

    cmake_lint/test/expect_lint.cmake:00: [C0301] Line too long (92/80)
    cmake_lint/test/expect_lint.cmake:02: [C0303] Trailing whitespace
    cmake_lint/test/expect_lint.cmake:04: [C0327] Wrong line ending (windows)
    cmake_lint/test/expect_lint.cmake:08,00: [C0111] Missing docstring on function or macro declaration
    cmake_lint/test/expect_lint.cmake:08,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:08,09: [C0103] Invalid function name "BAD_FUNCTION_NAME"
    cmake_lint/test/expect_lint.cmake:13,00: [C0112] Empty docstring on function or macro declaration
    cmake_lint/test/expect_lint.cmake:13,06: [C0103] Invalid function name "bad_macro_name"
    cmake_lint/test/expect_lint.cmake:17,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:24,10: [C0103] Invalid loopvar name "LOOPVAR3"
    cmake_lint/test/expect_lint.cmake:30,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:30,27: [E1120] Missing required positional argument
    cmake_lint/test/expect_lint.cmake:30,33: [E1120] Missing required positional argument
    cmake_lint/test/expect_lint.cmake:32,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:32,46: [E1122] Duplicate keyword argument VERSION
    cmake_lint/test/expect_lint.cmake:34,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:34,19: [E1120] Missing required positional argument
    cmake_lint/test/expect_lint.cmake:36,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:38,02: [C0114] Form descriminator hidden behind variable dereference
    cmake_lint/test/expect_lint.cmake:42,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:43,02: [E1126] Invalid form descriminator
    cmake_lint/test/expect_lint.cmake:47,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:47,19: [C0113] Missing COMMENT in statement which allows it
    cmake_lint/test/expect_lint.cmake:47,19: [E1125] Missing required keyword argument COMMAND
    cmake_lint/test/expect_lint.cmake:49,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:49,18: [C0113] Missing COMMAND in statement which allows it
    cmake_lint/test/expect_lint.cmake:49,18: [C0113] Missing COMMENT in statement which allows it
    cmake_lint/test/expect_lint.cmake:51,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:51,05: [E1120] Missing required positional argument
    cmake_lint/test/expect_lint.cmake:53,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:54,05: [C0114] Form descriminator hidden behind variable dereference
    cmake_lint/test/expect_lint.cmake:56,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:56,05: [E1126] Invalid form descriminator
    cmake_lint/test/expect_lint.cmake:58,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:58,00: [E0103] break outside of loop
    cmake_lint/test/expect_lint.cmake:58,00: [W0101] Unreachable code
    cmake_lint/test/expect_lint.cmake:60,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:60,00: [E0103] continue outside of loop
    cmake_lint/test/expect_lint.cmake:60,00: [W0101] Unreachable code
    cmake_lint/test/expect_lint.cmake:64,02: [C0201] Consider replacing custom parser logic with cmake_parse_arguments
    cmake_lint/test/expect_lint.cmake:75,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:75,18: [C0321] Multiple statements on a single line
    cmake_lint/test/expect_lint.cmake:77,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:80,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:83,13: [E0109] Invalid argument name "arg-name" in function/macro definition
    cmake_lint/test/expect_lint.cmake:88,17: [E0108] Duplicate argument name arg in function/macro definition
    cmake_lint/test/expect_lint.cmake:93,17: [C0202] Argument name ARG differs from existing argument only in case
    cmake_lint/test/expect_lint.cmake:97,00: [C0305] too many newlines between statements
    cmake_lint/test/expect_lint.cmake:97,00: [W0101] Unreachable code
    cmake_lint/test/expect_lint.cmake:102,00: [R0911] Too many return statements 17/6
    cmake_lint/test/expect_lint.cmake:102,00: [R0912] Too many branches 17/12
    cmake_lint/test/expect_lint.cmake:102,00: [R0913] Too many named arguments 6/5
    cmake_lint/test/expect_lint.cmake:102,00: [R0915] Too many statements 65/50
    cmake_lint/test/expect_lint.cmake:134,04: [C0103] Invalid CACHE variable name "MyGlobalVar"
    cmake_lint/test/expect_lint.cmake:137,04: [C0103] Invalid INTERNAL variable name "MY_INTERNAL_VAR"
    cmake_lint/test/expect_lint.cmake:140,04: [C0103] Invalid directory variable name "_INVALID_PRIVATE_NAME"
    cmake_lint/test/expect_lint.cmake:141,04: [C0103] Invalid directory variable name "invalid_public_name"
    cmake_lint/test/expect_lint.cmake:143,06: [C0103] Invalid local variable name "INVALID_LOCAL_NAME"
    cmake_lint/test/expect_lint.cmake:146: [C0304] Final newline missing

.. dynamic: lint-out-end
