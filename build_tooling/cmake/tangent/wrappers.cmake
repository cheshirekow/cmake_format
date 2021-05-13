# Split a list into named arguments in the current scope.
#
# Example:
# ~~~
# set(_mylist foo bar baz 1 2 3)
# EXPLODE(_mylist _var1 _var2 _var3)
# message(" var1: ${_var1}\n" " var2: ${_var2}\n" " var3: ${_var3}\n")
# ~~~
#
# Which will output:
# ~~~
#  var1: foo
#  var2: bar
#  var3: baz
# ~~~
macro(EXPLODE listname)
  set(_args ${ARGN})
  list(LENGTH "${listname}" _list_len)
  list(LENGTH _args _args_len)

  if("${_args_len}" LESS "${_list_len}")
    message(
      FATAL_ERROR
        " Can't EXPLODE ${_args_len} elements into ${_list_len} elements:\n"
        " ${_args}")
  endif()

  set(_idx "0")
  foreach(varname ${ARGN})
    list(GET ${listname} ${_idx} ${varname})
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

function(string_repeat value count outvar)
  unset(_local)
  math(EXPR range_end "${count} - 1")
  foreach(_ RANGE ${range_end})
    set(_local "${_local}${value}")
  endforeach()
  set(${outvar}
      ${_local}
      PARENT_SCOPE)
endfunction()

# Backport list(FILTER ...) to cmake < 3.6
function(list_filter listname)
  set(localcopy ${${listname}})
  if("${CMAKE_VERSION}" VERSION_GREATER "3.5.999")
    # cmake-lint: disable=E1120
    list(FILTER localcopy ${ARGN})
  else()
    cmake_parse_arguments(_args "" "REGEX" "" ${ARGN})
    explode(_args_UNPARSED_ARGUMENTS _mode)

    set(buffer)
    if("${_mode}" STREQUAL "INCLUDE")
      foreach(elem ${localcopy})
        if("${elem}" MATCHES "${_args_REGEX}")
          list(APPEND buffer "${elem}")
        endif()
      endforeach()
    else()
      foreach(elem ${localcopy})
        if(NOT "${elem}" MATCHES "${_args_REGEX}")
          list(APPEND buffer "${elem}")
        endif()
      endforeach()
    endif()
    set(localcopy ${buffer})
  endif()
  set(${listname}
      ${localcopy}
      PARENT_SCOPE)
endfunction()

# Wraps `execute_process` and reports error if any command in the list of
# commands fails.
function(check_call)
  cmake_parse_arguments(_args "" "OUTPUT_VARIABLE;ERROR_VARIABLE" "" ${ARGN})

  set(request_results_list)
  if("${CMAKE_VERSION}" VERSION_GREATER "3.9.999")
    set(request_results_list RESULTS_VARIABLE results)
  endif()

  set(results)
  execute_process(
    ${_args_UNPARSED_ARGUMENTS}
    OUTPUT_VARIABLE stdout
    ERROR_VARIABLE stderr
    RESULT_VARIABLE result ${request_results_list})

  set(kwargs
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
  string(REPLACE ";" "|" kwargs "${kwargs}")
  set(buffer ${_args_UNPARSED_ARGUMENTS})

  # Turn the cmake list into a regular string with '%' as an item separator
  string(REPLACE ";" "%" buffer "${buffer}")
  # Split the string at keyword boundaries
  string(REGEX REPLACE "\\%(${kwargs})" ";\\1" buffer "${buffer}")
  # Remove list items that aren't COMMAND
  set(buffer2 ${buffer})
  list_filter(buffer2 INCLUDE REGEX "COMMAND%.*")
  # Save the list of commands
  set(cmds "${buffer2}")

  set(idx "0")
  foreach(result ${results})
    if(NOT "${result}" EQUAL "0")
      list(GET cmds ${idx} cmdstr)
      string(REPLACE "COMMAND%" "" cmdstr "${cmdstr}")
      string(REPLACE "%" " " cmdstr "${cmdstr}")
      message(FATAL_ERROR " Failed to execute command ${idx}:\n"
                          "   ${cmdstr}\n   ${stderr}")
    endif()
    math(EXPR idx "${idx} + 1}")
  endforeach()

  if(NOT "${result}" EQUAL "0")
    string(REPLACE "COMMAND%" "\n  " cmdlines "${cmds}")
    string(REPLACE "%" " " cmdlines "${cmdlines}")
    message(FATAL_ERROR " Failed to execute one or more command:\n"
                        "  ${cmdlines}\n" "  ${stderr}")
  endif()

  if(_args_OUTPUT_VARIABLE)
    set(${_args_OUTPUT_VARIABLE}
        ${stdout}
        PARENT_SCOPE)
  endif()
  if(_args_ERROR_VARIABLE)
    set(${_args_ERROR_VARIABLE}
        ${stderr}
        PARENT_SCOPE)
  endif()
endfunction()

# Executes a python oneline using `execute_process` and reports error if the
# command failed
function(check_pyoneline)
  cmake_parse_arguments(_args "" "OUTPUT_VARIABLE;ERROR_VARIABLE" "" ${ARGN})

  # Escape semicolons in the cmake list, the resulting string will contain \\\;
  # for each semicolon. When we pass this into check_call the escape sequences
  # will be interpreted, resulting in \; within the `COMMAND` argument to
  # execute_process.
  string(REPLACE ";" "\\\\\\;" _oneline "${_args_UNPARSED_ARGUMENTS}")

  set(_pyonline ${ARGN})
  check_call(
    # NOTE(josh): cmake concats lines using semicolon, which is the same
    # separator that python expects, so we don't need to do any special
    # processing. The cmake list-concat gives us a python oneliner for free.
    COMMAND python -Bc "${_oneline}"
    OUTPUT_VARIABLE stdout
    ERROR_VARIABLE stderr
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_STRIP_TRAILING_WHITESPACE)

  if(_args_OUTPUT_VARIABLE)
    set(${_args_OUTPUT_VARIABLE}
        ${stdout}
        PARENT_SCOPE)
  endif()
  if(_args_ERROR_VARIABLE)
    set(${_args_ERROR_VARIABLE}
        ${stderr}
        PARENT_SCOPE)
  endif()
endfunction()

# Get a list of all known properties
check_call(COMMAND ${CMAKE_COMMAND} --help-property-list
           OUTPUT_VARIABLE _propslist)
# Replace newlines with list separator
string(REGEX REPLACE "[\n ]+" ";" _propslist "${_propslist}")
set(KNOWN_PROPERTIES ${_propslist})

function(tangent_addtest)
  cmake_parse_arguments(_args "" "NAME;WORKING_DIRECTORY"
                        "COMMAND;CONFIGURATIONS;DEPENDS;LABELS" ${ARGN})

  add_test(
    NAME ${_args_NAME}
    COMMAND ${_args_COMMAND}
    WORKING_DIRECTORY ${_args_WORKING_DIRECTORY}
    CONFIGURATIONS ${_args_CONFIGURATIONS})
  if(args_LABELS)
    set_property(
      TEST ${_args_NAME}
      APPEND
      PROPERTY LABELS ${args_LABELS})
  endif()
  add_custom_target(
    runtest.${_args_NAME}
    DEPENDS ${_args_DEPENDS}
    COMMAND ${_args_COMMAND}
    WORKING_DIRECTORY ${_args_WORKING_DIRECTORY})
  add_dependencies(best-test runtest.${_args_NAME})

endfunction()

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
# *INCS*: a list of include directories that should be added using
# target_include_dirs
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
  set(flags)
  set(oneargs)
  set(multiargs INC LIBDIRS SRCS DEPS PKGDEPS PROPERTIES)
  cmake_parse_arguments(_args "${flags}" "${oneargs}" "${multiargs}" ${ARGN})

  add_library(${target_name} ${_args_UNPARSED_ARGUMENTS} ${_args_SRCS})
  if(_args_INC)
    target_include_directories(${target_name} ${_args_INC})
  endif()
  if(_args_DEPS)
    list(GET _args_DEPS 0 dep0)
    if(NOT "${_dep0}" MATCHES "(PUBLIC)|(PRIVATE)|(INTERFACE)")
      list(INSERT _args_DEPS 0 "PUBLIC")
    endif()
    target_link_libraries(${target_name} ${_args_DEPS})
  endif()
  if(_args_PKGDEPS)
    target_pkg_depends(${target_name} ${_args_PKGDEPS})
  endif()
  if(_args_PROPERTIES)
    # cmake-lint: disable=E1120
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
  set(flags ADD_RUNTARGET)
  set(oneargs)
  set(multiargs
      INC
      LIBDIRS
      SRCS
      DEFS
      DEPS
      PKGDEPS
      PROPERTIES)
  cmake_parse_arguments(_args "${flags}" "${oneargs}" "${multiargs}" ${ARGN})

  add_executable(${target_name} ${_args_UNPARSED_ARGUMENTS} ${_args_SRCS})
  if(_args_INC)
    target_include_directories(${target_name} ${_args_INC})
  endif()
  if(_args_DEPS)
    target_link_libraries(${target_name} PUBLIC ${_args_DEPS})
  endif()
  if(_args_PKGDEPS)
    target_pkg_depends(${target_name} ${_args_PKGDEPS})
  endif()
  if(_args_PROPERTIES)
    # cmake-lint: disable=E1120
    set_target_properties(${target_name} PROPERTIES ${_args_PROPERTIES})
  endif()
  if(_args_DEFS)
    target_compile_definitions(${target_name} ${_args_DEFS})
  endif()

  if(_args_ADD_RUNTARGET)
    add_custom_target(
      run.${target_name}
      COMMAND ${target_name}
      WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
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
  set(flags)
  set(oneargs WORKING_DIRECTORY)
  set(multiargs ARGV TEST_DEPS LABELS)
  cmake_parse_arguments(args "${flags}" "${oneargs}" "${multiargs}" ${ARGN})

  set(cmd $<TARGET_FILE:${target_name}> ${args_ARGV})
  cc_binary(${target_name} ${args_UNPARSED_ARGUMENTS})

  if(NOT args_WORKING_DIRECTORY)
    set(args_WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endif()

  if(args_TEST_DEPS)
    add_custom_target(testdeps.${target_name} DEPENDS ${args_TEST_DEPS})
    add_dependencies(testdeps testdeps.${target_name})
  endif()

  tangent_addtest(
    NAME ${target_name}
    COMMAND ${cmd}
    DEPENDS ${args_TEST_DEPS}
    WORKING_DIRECTORY ${args_WORKING_DIRECTORY}
    LABELS ${args_LABELS})

endfunction()

# Given a list of variables in the current scope, assign their value to a
# variable of the same name in the parent scope
macro(RETURNVARS)
  foreach(varname ${ARGN})
    set(${varname}
        "${${varname}}"
        PARENT_SCOPE)
  endforeach()
endmacro()

set_property(GLOBAL PROPERTY SEMVER_INCLUDENO 0)
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
# Assigns into the calling scope a variable with the same name as `${macro}` the
# value of the version
function(get_version_from_header headerpath macro)
  get_property(_includeno GLOBAL PROPERTY SEMVER_INCLUDENO)
  math(EXPR _includeno "${_includeno} + 1")
  set_property(GLOBAL PROPERTY SEMVER_INCLUDENO ${_includeno})
  set(stubfile ${CMAKE_CURRENT_BINARY_DIR}/semver-${_includeno}.cmake)

  if(NOT IS_ABSOLUTE ${headerpath})
    set(headerpath ${CMAKE_CURRENT_SOURCE_DIR}/${headerpath})
  endif()

  execute_process(
    COMMAND python -B ${TANGENT_TOOLING}/get_version_from_header.py #
            --outfile ${stubfile} ${macro} ${headerpath}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    RESULT_VARIABLE _retcode
    OUTPUT_VARIABLE _stdout
    ERROR_VARIABLE _stderr)
  if(NOT "${_retcode}" EQUAL "0")
    message(
      FATAL_ERROR " Failed to extract version number from"
                  " ${headerpath}: ${_retcode}\n" " ${_stdout}\n" " ${_stderr}")
  endif()
  include(${stubfile} RESULT_VARIABLE _result)
  if(_result STREQUAL NOTFOUND)
    message(FATAL_ERROR "Failed to include stubfile ${stubfile}")
  endif()

  string(REGEX MATCH "(.*)_VERSION" _match "${macro}")
  if(_match)
    set(prefix ${CMAKE_MATCH_1})
  else()
    message(
      FATAL_ERROR "Header version macro '${macro}' does not end in _VERSION")
  endif()

  returnvars(${prefix}_VERSION ${prefix}_API_VERSION ${prefix}_SO_VERSION)
endfunction()

# map package name to source directory
set(_package_pairs
    "argue\;argue" #
    "libtangent-util\;tangent/util" #
    "libtangent-json\;tangent/json" #
    "gtangent\;gtangent" #
    "gtangentmm\;gtangentmm" #
)
foreach(pair ${_package_pairs})
  explode(pair _package_name _repodir)
  set(TANGENT_PACKAGE_SOURCEDIR_${_package_name} ${_repodir})
endforeach()

# Wraps a call to find_package() for a tangent supplied cmake package and
# pre-empt the call to find_package() if the package exists locally in the
# sparse checkout,
function(find_tangent_package package_name)
  set(repodir ${TANGENT_PACKAGE_SOURCEDIR_${package_name}})
  if(EXISTS ${CMAKE_SOURCE_DIR}/${repodir})
    return()
  endif()
  find_package(${package_name} ${ARGN})
endfunction()

# Tunable verbose logging
function(vlog level)
  if(NOT DEFINED TANGENT_VERBOSE_LEVEL)
    return()
  endif()
  if("${level}" GREATER ${TANGENT_VERBOSE_LEVEL})
    return()
  endif()
  message(STATUS ${ARGN})
endfunction()

# Glob the current source directory for any children that have listfiles, and
# add them.
function(glob_subdirs)
  # NOTE(josh): search through the list of child directories and add any that
  # actually contain a listfile. While globs are evil, this is necessary for
  # sparse checkouts. We can and should correctly add dependencies for this glob
  # in order to retrigger cmake.
  file(
    GLOB children
    RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/*)
  foreach(child ${children})
    set(candidate ${CMAKE_CURRENT_SOURCE_DIR}/${child}/CMakeLists.txt)
    if(EXISTS ${candidate})
      file(RELATIVE_PATH relpath_candidate "${CMAKE_SOURCE_DIR}" "${candidate}")
      vlog(1 "Enabling subdirectory ${relpath_candidate}")
      add_subdirectory(${child})
    endif()
  endforeach()
endfunction()

# If this build system was generated on travis, the include a rule to decrypt
# the given file to the given location.
function(travis_decrypt tgtfile srcfile keyid)
  get_filename_component(_filename ${tgtfile} NAME)
  if(IS_TRAVIS_CI)
    add_custom_command(
      OUTPUT ${tgtfile}
      DEPENDS ${srcfile}
      COMMAND
        # cmake-format: off
        openssl aes-256-cbc
        # NOTE(josh): we could use $ENV{...} but then we end up with the
        # actual encryption key in the command line... which might show up
        # in logs or error messages.
        -K "\$\${encrypted_${keyid}_key}"
        -iv "\$\${encrypted_${keyid}_iv}"
        -in ${srcfile}
        -out ${tgtfile}
        -d
        # cmake-format: on
      COMMAND chmod 0600 ${tgtfile}
      COMMENT "Decrypting ${_filename}")
  endif()
endfunction()

# Uses the swift command line client to fetch
function(tangent_fetchobj uuid filename)
  add_custom_command(
    OUTPUT ${filename}
    COMMAND
      # cmake-format: off
      swift
      "--os-auth-url=https://auth.cloud.ovh.net/v3/"
      "--os-identity-api-version=3"
      "--os-region-name=BHS"
      "--os-tenant-id=b5e0ef36abcb498b890d84b61555f063"
      "--os-tenant-name=0728979165260176"
      "--os-username=user-px7eRuuMs4hy"
      "--os-password=HHScMqa9DHaAphNqQx6YpaRsMVE4AakH"
      # cmake-format: on
      download tangent-build ${uuid} -o ${filename}
    COMMENT "Downloading ${filename}")
endfunction()

function(tangent_unzip targetname zipfile)
  cmake_parse_arguments(args "ALL" "WORKING_DIRECTORY" "OUTPUT" ${ARGN})
  set(zip_outputs)
  if(args_WORKING_DIRECTORY)
    foreach(outfile ${args_OUTPUT})
      list(APPEND zip_outputs "${args_WORKING_DIRECTORY}/${outfile}")
    endforeach()
  else()
    set(zip_outputs ${args_OUTPUT})
  endif()

  add_custom_command(
    DEPENDS ${zipfile}
    OUTPUT ${zip_outputs}
    COMMAND ${CMAKE_COMMAND} -E tar xf ${zipfile}
    WORKING_DIRECTORY ${args_WORKING_DIRECTORY}
    COMMENT "Unzipping ${zipfile}")

  set(maybe_ALL)
  if(${args_ALL})
    set(maybe_ALL "ALL")
  endif()
  add_custom_target(
    ${targetname}
    ${maybe_ALL}
    DEPENDS ${zip_outputs})

endfunction()

function(tangent_verify_image target_prefix imgfile reference_hash)
  tangent_addtest(
    NAME phash-verify-${target_prefix}${imgfile}
    COMMAND $<TARGET_FILE:phash-exe> verify ${imgfile} ${reference_hash}
    DEPENDS phash-exe
    WORKING_DIRECTORY ${args_WORKING_DIRECTORY}
    LABELS ${args_LABELS})
endfunction()

# Copy a file from the source tree to the binary tree
function(copybin target)
  unset(_copyfiles)
  foreach(filename ${ARGN})
    if(NOT "${CMAKE_CURRENT_SOURCE_DIR}" STREQUAL "${CMAKE_CURRENT_BINARY_DIR}")
      add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
        COMMAND
          ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
          ${CMAKE_CURRENT_BINARY_DIR}/${filename})
      list(APPEND _copyfiles ${CMAKE_CURRENT_BINARY_DIR}/${filename})
    endif()
  endforeach()
  add_custom_target(${target} DEPENDS ${_copyfiles})
endfunction()

# Generate .h and .c resource data to embed in an application
function(gresource args_BASENAME args_XMLFILE)
  cmake_parse_arguments(args "" "SRCDIR" "DEPENDS" ${ARGN})

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${args_BASENAME}.h
    DEPENDS ${args_XMLFILE} ${args_DEPENDS}
    COMMAND
      glib-compile-resources --sourcedir=${args_SRCDIR} --generate
      ${CMAKE_CURRENT_SOURCE_DIR}/${args_XMLFILE} --target=${args_BASENAME}.h)

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${args_BASENAME}.c
    DEPENDS ${args_XMLFILE} ${args_DEPENDS}
    COMMAND
      glib-compile-resources --sourcedir=${args_SRCDIR} --generate
      ${CMAKE_CURRENT_SOURCE_DIR}/${args_XMLFILE} --target=${args_BASENAME}.c)
endfunction()

# Use inkscape to extract a subset of an SVG into it's own SVG file. This is
# useful for working on multiple icons in a single SVG and then splitting them
# into separate SVGs at build time
function(tangent_extract_svg)
  cmake_parse_arguments(args "" "OUTPUT;SRC;EXPORT" "" ${ARGN})
  add_custom_command(
    OUTPUT ${args_OUTPUT}
    DEPENDS icons.svg
    # NOTE(josh): rsvg is completely broken COMMAND rsvg-convert
    # --export-id="${args_EXPORT}" --format=svg --output ${args_OUTPUT}
    # ${args_SRC}
    COMMAND inkscape "--export-plain-svg=${args_OUTPUT}"
            "--export-id=${args_EXPORT}" --export-id-only ${args_SRC})
endfunction()

function(protostruct_gen args_PROTO)
  cmake_parse_arguments(args "" "" "ONLY" ${ARGN})

  if(NOT ${args_PROTO} MATCHES "(.*).proto")
    message(FATAL_ERROR "invalid protofile ${args_PROTO}")
  endif()
  set(basename ${CMAKE_MATCH_1})

  unset(outs)
  unset(only_flags)
  if(args_ONLY)
    set(only_flags "--only" ${args_ONLY})
    foreach(groupname ${args_ONLY})
      if(groupname STREQUAL "cpp-simple")
        list(APPEND outs #
             ${CMAKE_CURRENT_BINARY_DIR}/${basename}-simple.h
             ${CMAKE_CURRENT_BINARY_DIR}/${basename}-simple.cc)
      else()
        message(FATAL_ERROR "protostruct_gen not implemented for ${groupname}")
      endif()
    endforeach()
  else()
    message(FATAL_ERROR "protostruct_gen not implemented without ONLY")
  endif()

  add_custom_command(
    OUTPUT ${outs}
    DEPENDS ${args_PROTO} protostruct
    COMMAND
      # cmake-format: off
      $<TARGET_FILE:protostruct>
      ${args_PROTO}
      --proto-path ${CMAKE_CURRENT_SOURCE_DIR}
      --outfile ${CMAKE_CURRENT_BINARY_DIR}/${basename}.pb3
      --cpp-out ${CMAKE_CURRENT_BINARY_DIR}
      ${only_flags}
      # cmake-format: on
    COMMAND # cmake-format: off
      clang-format-8 -i -style=File ${outs}
      # cmake-format: on
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
endfunction()
