# test: line-too-long
# expect: C0301@1
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

# test: missing-required
# expect: E1120,E1120
set(VARNAME varvalue CACHE STRING)

# test: duplicate-kwarg
# expect: E1122
cmake_minimum_required_version(VERSION 2.8.11 VERSION 3.16)

# test: add-custom-command-missing-required-positional
# expect: E1120
add_custom_command()

# test: add-custom-command-hidden-descriminator
# expect: C0114
set(_form TARGET PRE_BUILD)
add_custom_command(
  ${form}
  COMMAND echo "hello"
  COMMENT "echo hello")

# test: add-custom-command-invalid-descriminator
# expect: E1126
add_custom_command(
  TARGRET PRE_BUILD
  COMMAND echo "hello"
  COMMENT "echo hello")

# test: add-custom-command-missing-required-kwarg
# expect: C0113,E1125
add_custom_command(OUTPUT foo)

# test: file-missing-required
# expect: E1120
file()

# test: file-hidden-descriminator
# expect: C0114
set(_form TOUCH)
file(${form} foo.py)

# test: file-invalid-descriminator
# expect: E1126
file(TOUCHE foo.py)

# test: break-not-in-loop
# expect: E0103
break()

# test: continue-not-in-loop
# expect: E0103
continue()

# test: fundef-contains-custom-parser
# expect: C0201
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

# test: multiple-statements-single-line
# expect: C0321
set(_foo "hello") set(_bar "goodbye")

# test: too-much-spacing-between-statements
# expect: C0305
set(_foo "hello")


set(_bar "goodbye")

# test: invalid-argument-name
# expect: E0109
# foo: docstring
function(foo "arg-name")
  # pass
endfunction()

# test: duplicate-argument-name
# expect: E0108
# foo: docstring
function(foo arg arg)
  # pass
endfunction()

# test: argname-differs-only-by-case
# expect: C0202
# foo: docstring
function(foo arg ARG)
  # pass
endfunction()

# test: unreachable-code
# expect: W0101
return()
message("This code is unreachable")

# test: refactor-fun
# expect: R0913,R0911,R0912,R0915
# cmake-lint: disable=E0109,C0321
# foo:docstring, too many arguments
function(foo a0 a1 a2 a3 a4 a5)

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

# test: invalid-varnames
# expect: C0103@3,C0103@6,C0103@9,C0103@10,C0103@12
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

# test: set-wrong-case
# expect: W0105
set(CMAKE_Cxx_STANDARD "11")

# test: list-wrong-case
# expect: W0105
list(APPEND CMAKE_Cxx_STANDARD "11")

# test: uses-var-wrong-case
# expect: W0105
message("Using C++ standard ${CMAKE_Cxx_STANDARD}")

# test: almost-varref
# expect: W0106,W0106,W0106
message("$CMAKE_INSTALL_PREFIX}")
message("{CMAKE_INSTALL_PREFIX}")
message("${CMAKE_INSTALL_PREFIX")

# test: missing-final-newline
# expect: C0304
# This file is missing a final newline