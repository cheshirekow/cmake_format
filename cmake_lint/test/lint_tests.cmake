# test: line-too-long
# expect: C0301
# The line is too long and exceeds the default 80 character column limit enforced cmake-lint

# test: trailing-whitespace
# expect: C0303
# This line has trailing whitespace   

# test: line-endings
# expect: C0327
# This line has the wrong line endings

# test: function-defn
# expect: C0111,C0103

function(BAD_FUNCTION_NAME badArgName good_arg_name)
  # Function names should be lower case
endfunction()

# test: macro-defn
# expect: C0112,C0103
#
macro(bad_macro_name badArgName good_arg_name)
  # Macro names should be upper case
endmacro()

# test: local-disable
# expect: C0103@8
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

# test: missing-final-newline
# expect: C0304
# This file is missing a final newline