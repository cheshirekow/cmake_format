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

file()

set(_form TOUCH)
file(${form} foo.py)

file(TOUCHE foo.py)

file(GLOB foo LIST_DIRECTORIES false *)

file(GLOB_RECURSE foo CONFIGURE_DEPENDS *.cpp)

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

set(CMAKE_Cxx_STANDARD "11")

list(APPEND CMAKE_Cxx_STANDARD "11")

message("Using C++ standard ${CMAKE_Cxx_STANDARD}")

message("$CMAKE_INSTALL_PREFIX}")
message("{CMAKE_INSTALL_PREFIX}")
message("${CMAKE_INSTALL_PREFIX")

# This file is missing a final newline