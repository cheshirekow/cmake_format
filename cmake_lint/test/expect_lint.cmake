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