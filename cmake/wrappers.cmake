# Split a list into named arguments in the current scope.
#
# Example:
# ~~~
# set(_mylist foo bar baz 1 2 3)
# explode(_mylist _var1 _var2 _var3)
# message(" var1: ${_var1}\n" " var2: ${_var2}\n" " var3: ${_var3}\n")
# ~~~
#
# Which will output:
# ~~~
#  var1: foo
#  var2: bar
#  var3: baz
# ~~~
macro(explode _list)
  set(_args ${ARGN})
  list(LENGTH "${_list}" _list_len)
  list(LENGTH _args _args_len)

  if("${_args_len}" LESS "${_list_len}")
    message(
      FATAL_ERROR
        " Can't explode ${_args_len} elements into ${_list_len} elements:\n"
        " ${_args}")
  endif()

  set(_idx "0")
  foreach(_varname ${ARGN})
    list(GET ${_list} ${_idx} ${_varname})
    math(EXPR _idx "${_idx} + 1}")
  endforeach()
endmacro()

# Join a list of strings into a single string
#
# usage:
# ~~~
# join(<outvar> [GLUE <glue>] [arg1 [arg2 [arg3 [...]]]])
# ~~~
function(join outvar)
  cmake_parse_arguments(args "" "GLUE" "" ${ARGN})
  set(joined)
  foreach(part ${args_UNPARSED_ARGUMENTS})
    set(joined "${joined}${args_GLUE}${part}")
  endforeach()
  set(${outvar}
      "${joined}"
      PARENT_SCOPE)
endfunction()

# Backport list(FILTER ...) to cmake < 3.6
function(list_filter _listname)
  set(_localcopy ${${_listname}})
  if("${CMAKE_VERSION}" VERSION_GREATER "3.5.999")
    list(FILTER _localcopy ${ARGN})
  else()
    cmake_parse_arguments(_args "" "REGEX" "" ${ARGN})
    explode(_args_UNPARSED_ARGUMENTS _mode)

    set(_buffer)
    if("${_mode}" STREQUAL "INCLUDE")
      foreach(_elem ${_localcopy})
        if("${_elem}" MATCHES "${_args_REGEX}")
          list(APPEND _buffer "${_elem}")
        endif()
      endforeach()
    else()
      foreach(_elem ${_localcopy})
        if(NOT "${_elem}" MATCHES "${_args_REGEX}")
          list(APPEND _buffer "${_elem}")
        endif()
      endforeach()
    endif()
    set(_localcopy ${_buffer})
  endif()
  set(${_listname}
      ${_localcopy}
      PARENT_SCOPE)
endfunction()

# Wraps `execute_process` and reports error if any command in the list of
# commands fails.
function(check_call)
  cmake_parse_arguments(_args "" "OUTPUT_VARIABLE;ERROR_VARIABLE" "" ${ARGN})

  set(_request_results_list)
  if("${CMAKE_VERSION}" VERSION_GREATER "3.9.999")
    set(_request_results_list RESULTS_VARIABLE _results)
  endif()

  set(_results)
  execute_process(
    ${_args_UNPARSED_ARGUMENTS}
    OUTPUT_VARIABLE _stdout
    ERROR_VARIABLE _stderr
    RESULT_VARIABLE _result ${_request_results_list})

  set(_kwargs
      COMMAND
      WORKING_DIRECTORY
      TIMEOUT
      RESULT_VARIABLE
      RESULTS_VARIABLE
      OUTPUT_VARIABLE
      ERROR_VARIABLE
      INPUT_FILE
      OUTPUT_FILE
      ERROR_FILE
      OUTPUT_QUIET
      ERROR_QUIET
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_STRIP_TRAILING_WHITESPACE
      ENCODING)
  string(REPLACE ";" "|" _kwargs "${_kwargs}")
  set(_buffer ${_args_UNPARSED_ARGUMENTS})

  # Turn the cmake list into a regular string with '%' as an item separator
  string(REPLACE ";" "%" _buffer "${_buffer}")
  # Split the string at keyword boundaries
  string(REGEX REPLACE "\\%(${_kwargs})\\%" ";\\1%" _buffer "${_buffer}")
  # Remove list items that aren't COMMAND
  set(_buffer2 ${_buffer})
  list_filter(_buffer2 INCLUDE REGEX "COMMAND%.*")
  # Save the list of commands
  set(_cmds "${_buffer2}")

  set(_idx "0")
  foreach(_result ${_results})
    if(NOT "${_result}" EQUAL "0")
      list(GET _cmds ${_idx} _cmdstr)
      string(REPLACE "COMMAND%" "" _cmdstr "${_cmdstr}")
      string(REPLACE "%" " " _cmdstr "${_cmdstr}")
      message(FATAL_ERROR " Failed to execute command ${_idx}:\n"
                          "   ${_cmdstr}\n   ${_stderr}")
    endif()
    math(EXPR _idx "${_idx} + 1}")
  endforeach()

  if(NOT "${_result}" EQUAL "0")
    string(REPLACE "COMMAND%" "\n  " _cmdlines "${_cmds}")
    string(REPLACE "%" " " _cmdlines "${_cmdlines}")
    message(FATAL_ERROR " Failed to execute one or more command:\n"
                        "  ${_cmdlines}\n" "  ${_stderr}")
  endif()

  if(_args_OUTPUT_VARIABLE)
    set(${_args_OUTPUT_VARIABLE}
        ${_stdout}
        PARENT_SCOPE)
  endif()
  if(_args_ERROR_VARIABLE)
    set(${_args_ERROR_VARIABLE}
        ${_stderr}
        PARENT_SCOPE)
  endif()
endfunction()

# Get a list of all known properties
check_call(COMMAND ${CMAKE_COMMAND} --help-property-list
           OUTPUT_VARIABLE _propslist)
# Replace newlines with list separator
string(REGEX REPLACE "[\n ]+" ";" _propslist "${_propslist}")
set(KNOWN_PROPERTIES ${_propslist})

# Wraps add_library and provides additional keyword options that translate into
# additional calls to target_link_libraries, target_set_properties, etc. Usage:
# ~~~
#   cc_library(<target-name> [STATIC|SHARED]
#     SRCS src1.cc src2.cc src3.cc
#     DEPS lib1 lib2 lib3)
# ~~~
#
# Keyword Arguments:
#
# *SRCS*: a list of source files that go into compilation. These translate to
# the positional arguments of add_library().
#
# *DEPS*: a list of libraries to link against. These should be names that cmake
# understands. They are passed as the positional arguments to
# target_link_libraires
#
# *PKGDEPS*: A list of pkg-config names that are dependencies of this
# executable. They are passed as positional arguments to target_pkg_depends
function(cc_library target_name)
  set(_flags)
  set(_oneargs)
  set(_multiargs SRCS DEPS PKGDEPS PROPERTIES)
  cmake_parse_arguments(_args "${_flags}" "${_oneargs}" "${_multiargs}" ${ARGN})

  add_library(${target_name} ${_args_UNPARSED_ARGUMENTS} ${_args_SRCS})
  if(_args_DEPS)
    target_link_libraries(${target_name} PUBLIC ${_args_DEPS})
  endif()
  if(_args_PKGDEPS)
    target_pkg_depends(${target_name} ${_args_PKGDEPS})
  endif()
  if(_args_PROPERTIES)
    set_target_properties(${target_name} PROPERTIES ${_args_PROPERTIES})
  endif()
endfunction()

# Wraps add_executable and provides additional keyword options that translate
# into additional calls to target_link_libraries, target_set_properties, etc.
# Usage:
# ~~~
#   cc_binary(<target-name>
#     SRCS src1.cc src2.cc src3.cc
#     DEPS lib1 lib2 lib3)
# ~~~
#
# Keyword Arguments:
#
# *SRCS*: a list of source files that go into compilation. These translate to
# the positional arguments of add_executable().
#
# *DEPS*: a list of libraries to link against. These should be names that cmake
# understands. They are passed as the positional arguments to
# target_link_libraires
#
# *PKGDEPS*: A list of pkg-config names that are dependencies of this
# executable. They are passed as positional arguments to target_pkg_depends
function(cc_binary target_name)
  set(_flags)
  set(_oneargs)
  set(_multiargs SRCS DEPS PKGDEPS PROPERTIES)
  cmake_parse_arguments(_args "${_flags}" "${_oneargs}" "${_multiargs}" ${ARGN})

  add_executable(${target_name} ${_args_UNPARSED_ARGUMENTS} ${_args_SRCS})
  if(_args_DEPS)
    target_link_libraries(${target_name} PUBLIC ${_args_DEPS})
  endif()
  if(_args_PKGDEPS)
    target_pkg_depends(${target_name} ${_args_PKGDEPS})
  endif()
  if(_args_PROPERTIES)
    set_target_properties(${target_name} PROPERTIES ${_args_PROPERTIES})
  endif()
endfunction()

# Wraps a pair of calls to cc_binary and add_test and provides additional
# keyword options that translate to additional calls to set_property
#
# Usage:
# ~~~
#   cc_test(<cc_binary()-spec>
#     ARGV --flag1 --flag2
#     TEST_DEPS file1 file2
#     WORKING_DIRECTORY <workdir>
#     LABELS label1 label2)
# ~~~
#
# In addition to creating the executable, this command will also create a target
# `run.<test-name>` which can be specified as a target to the build system. When
# specified as a build target, will ensure that all the depenencies are up-to-
# date before executing the test.
#
# The name of the test will match the name of the executable target.
#
# Keyword Arguments:
#
# *ARGV*: a list of additional command line options added to the command used
# for the test
#
# *TEST_DEPS*: additional file-level dependencies required to execute the test,
# such as golden data or resource files.
#
# *WORKING_DIRECTORY*: working directory where to execute the command
#
# *LABELS*: a list of ctest labels pased to set_property(TEST ...)
function(cc_test target_name)
  set(_flags)
  set(_oneargs WORKING_DIRECTORY)
  set(_multiargs ARGV TEST_DEPS LABELS)
  cmake_parse_arguments(_args "${_flags}" "${_oneargs}" "${_multiargs}" ${ARGN})

  set(_cmd $<TARGET_FILE:${target_name}> ${_args_ARGV})
  cc_binary(${target_name} ${_args_UNPARSED_ARGUMENTS})

  if(NOT _args_WORKING_DIRECTORY)
    set(_args_WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endif()

  if(_args_TEST_DEPS)
    add_custom_target(testdeps.${target_name} DEPENDS ${TEST_DEPS})
    add_dependencies(testdeps testdeps.${target_name})
  endif()

  add_custom_target(
    run.${target_name}
    COMMAND ${_cmd}
    DEPENDS ${_args_TEST_DEPS}
    WORKING_DIRECTORY ${_args_WORKING_DIRECTORY})

  add_test(
    NAME ${target_name}
    COMMAND ${_cmd}
    WORKING_DIRECTORY ${_args_WORKING_DIRECTORY})

  if(_args_LABELS)
    set_property(
      TEST ${target_name}
      APPEND
      PROPERTY LABELS ${_args_LABELS})
  endif()
endfunction()

macro(returnvars)
  foreach(varname ${ARGN})
    set(${varname}
        "${${varname}}"
        PARENT_SCOPE)
  endforeach()
endmacro()

# Get the version string by parsing a C++ header file. The version is expected
# to be in the form of:
#
# ~~~
# define FOO_VERSION \
#   { 0, 1, 0, "dev", 0 }
# ~~~
#
# Usage:
# ~~~
# get_version_from_header(<header-path> <macro>)
# ~~~
#
# Assigns into the calling scope a variable witht the same name as `${macro}`
# the value of the version
set_property(GLOBAL PROPERTY SEMVER_INCLUDENO 0)
function(get_version_from_header headerpath macro)
  get_property(_includeno GLOBAL PROPERTY SEMVER_INCLUDENO)
  math(EXPR _includeno "${_includeno} + 1")
  set_property(GLOBAL PROPERTY SEMVER_INCLUDENO ${_includeno})
  set(_stubfile ${CMAKE_CURRENT_BINARY_DIR}/semver-${_includeno}.cmake)

  if(NOT IS_ABSOLUTE ${headerpath})
    set(headerpath ${CMAKE_CURRENT_SOURCE_DIR}/${headerpath})
  endif()

  execute_process(
    COMMAND python -Bsm cmake.get_version_from_header --outfile ${_stubfile}
            ${macro} ${headerpath}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    RESULT_VARIABLE _retcode
    OUTPUT_VARIABLE _stdout
    ERROR_VARIABLE _stderr)
  if(NOT "${_retcode}" EQUAL "0")
    message(
      FATAL_ERROR " Failed to extract version number from"
                  " ${headerpath}: ${_retcode}\n" " ${_stdout}\n" " ${_stderr}")
  endif()
  include(${_stubfile} RESULT_VARIABLE _result)
  if(_result STREQUAL NOTFOUND)
    message(FATAL_ERROR "Failed to include stubfile ${_stubfile}")
  endif()

  string(REGEX MATCH "(.*)_VERSION" _match "${macro}")
  if(_match)
    set(_prefix ${CMAKE_MATCH_1})
  else()
    message(
      FATAL_ERROR "Header version macro '${macro}' does not end in _VERSION")
  endif()

  returnvars(${_prefix}_VERSION ${_prefix}_API_VERSION ${_prefix}_SO_VERSION)
endfunction()
