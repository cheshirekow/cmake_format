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

    # This file is missing a final newline
.. dynamic: lint-in-end

The output is:

.. dynamic: lint-out-begin

.. code:: text

    cmake_lint/test/expect_lint.cmake:00: [C0301] Line too long (92/80)
    cmake_lint/test/expect_lint.cmake:02: [C0303] Trailing whitespace
    cmake_lint/test/expect_lint.cmake:04: [C0327] Wrong line ending (windows)
    cmake_lint/test/expect_lint.cmake:08,00: [C0111] Missing docstring on function or macro declaration
    cmake_lint/test/expect_lint.cmake:08,09: [C0103] Invalid function name "BAD_FUNCTION_NAME"
    cmake_lint/test/expect_lint.cmake:13,00: [C0112] Empty docstring on function or macro declaration
    cmake_lint/test/expect_lint.cmake:13,06: [C0103] Invalid function name "bad_macro_name"
    cmake_lint/test/expect_lint.cmake:24,10: [C0103] Invalid loopvar name "LOOPVAR3"
    cmake_lint/test/expect_lint.cmake:30: [C0304] Final newline missing

.. dynamic: lint-out-end
