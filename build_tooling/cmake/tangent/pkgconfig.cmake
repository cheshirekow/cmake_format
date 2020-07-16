# Porcelain tools for using pkg config. Better than cmake's builtins.

# Execute pkg-config and store flags in the cache. Sets the variable `pkg_errno`
# in the parent scope to the return value of the subprocess call.
function(_pkg_query outvar arg)
  execute_process(
    COMMAND pkg-config --cflags-only-I ${arg}
    RESULT_VARIABLE _pkg_err
    OUTPUT_VARIABLE _pkg_out
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if(NOT _pkg_err EQUAL 0)
    set(pkg_errno
        1
        PARENT_SCOPE)
    return()
  endif()

  # Convert space-separated list to semicolon-separated cmake-list
  string(REGEX REPLACE " +" ";" _includes_raw "${_pkg_out}")

  set(PKG_${outvar}_INCLUDEDIRS_RAW
      ${_includes_raw}
      CACHE STRING "include directories for ${outvar}" FORCE)

  # Strip "-I" from include directories in the form of "-I/path/to"
  string(REGEX REPLACE "-I" "" _include_list "${_includes_raw}")

  set(PKG_${outvar}_INCLUDEDIRS
      ${_include_list}
      CACHE STRING "include directories for ${outvar}" FORCE)

  execute_process(
    COMMAND pkg-config --cflags-only-other ${arg}
    RESULT_VARIABLE _pkg_err
    OUTPUT_VARIABLE _pkg_out
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if(NOT _pkg_err EQUAL 0)
    set(pkg_errno
        1
        PARENT_SCOPE)
    return()
  endif()

  # Convert space-separated list to semicolon-separated cmake-list
  string(REGEX REPLACE " +" ";" _cflags_raw "${_pkg_out}")

  set(PKG_${outvar}_CFLAGS_RAW
      ${_cflags}
      CACHE STRING "cflags directories for ${outvar}" FORCE)

  # Convert some C++ specific flags into a generator expression that will
  # nullify during C compiles. Specifically match replace strings like
  # "-std=c++11" to "$<$<COMPILE_LANGUAGE:CXX>:-std=c++11>".
  string(REGEX REPLACE "(-std=[^;]+)" "$<$<COMPILE_LANGUAGE:CXX>:\\1>" _cflags
                       "${_cflags_raw}")

  set(PKG_${outvar}_CFLAGS
      ${_cflags}
      CACHE STRING "cflags for ${outvar}" FORCE)

  set(PKG_${outvar}_CFLAGS_RAW
      ${_includes_raw} ${_cflags_raw}
      CACHE STRING "raw cflags for ${outvar}" FORCE)

  execute_process(
    COMMAND pkg-config --libs-only-L ${arg}
    RESULT_VARIABLE _pkg_err
    OUTPUT_VARIABLE _pkg_out
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if(NOT _pkg_err EQUAL 0)
    set(pkg_errno
        1
        PARENT_SCOPE)
    return()
  endif()

  # Convert space-separated list to semicolon-separated cmake-list
  string(REGEX REPLACE " +" ";" _libdirs_raw "${_pkg_out}")

  # Remove -L prefix
  string(REGEX REPLACE "-L" "" _libdirs "${_libdirs_raw}")

  set(PKG_${outvar}_LIBDIRS
      ${_libdirs}
      CACHE STRING "library directories for ${outvar}" FORCE)

  execute_process(
    COMMAND pkg-config --libs-only-l ${arg}
    RESULT_VARIABLE _pkg_err
    OUTPUT_VARIABLE _pkg_out
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if(NOT _pkg_err EQUAL 0)
    set(pkg_errno
        1
        PARENT_SCOPE)
    return()
  endif()

  # Convert space-separated list to semicolon-separated cmake-list
  string(REGEX REPLACE " +" ";" _libs_raw "${_pkg_out}")

  # Convert space-separated list to semicolon-separated cmake-list Strip "-l"
  # from libraries in the form of "-lfilename" so that they are just "filename".
  # Cmake will add the -l.
  string(REGEX REPLACE "-l" "" _libs "${_libs_raw}")

  set(PKG_${outvar}_LIBS
      ${_libs}
      CACHE STRING "library directories for ${outvar}" FORCE)
  message(STATUS "PKG_${outvar}_LIBS: ${PKG_${outvar}_LIBS}")

  set(PKG_${outvar}_NAME
      ${arg}
      CACHE STRING "selected name which worked as an argument to pkg-config"
            FORCE)

  set(PKG_${outvar}_LDFLAGS_RAW
      ${_libdirs_raw} ${_libs_raw}
      CACHE STRING "raw ldflags for ${outvar}" FORCE)

  set(pkg_errno
      0
      PARENT_SCOPE)
endfunction()

# Execute pkg-config for each name in the list Usage
# _pkg_query_loop(<canonical_name> [<alt1> [<alt2> [...]]])
function(_pkg_query_loop name)
  if(PKG_${outvar}_FOUND)
    return()
  endif()
  set(outvar ${name})
  set(names ${ARGN})
  if(NOT names)
    set(names ${name})
  endif()

  set(pkg_errno 1)
  foreach(qname ${names})
    _pkg_query(${outvar} ${qname})
    if(pkg_errno EQUAL 0)
      set(PKG_${outvar}_FOUND
          TRUE
          CACHE BOOL "${outvar} was found" FORCE)
      return()
    endif()
  endforeach()

  set(PKG_${outvar}_FOUND
      FALSE
      CACHE BOOL "${outvar} was not found" FORCE)
endfunction()

# Find system packages using pkg-config.
#
# usage:
# ~~~
# pkg_find(PKG libfoo NAMES libfoo libfoo-1 libfoox
#          PKG libbar NAMES libarx
#          PKG libbaz)
# ~~~
#
# Execute pkg-config to get flags for each of the given library names. Each
# library is specified with a line `PKG <name> [NAMES <name0>, ...]`. If the
# library might have different names on different supported systems you may
# specify a list of names to attempt. The first one that `pkg-config` exists
# with `0` for will be used. If `NAMES` is provided, then `<name>` will not be
# attempted (so duplicate it if you want to). `<name>` will be used for the key
# in the pkg-config database cache.
function(pkg_find)
  # cmake-lint: disable=C0201,R0912
  set(state_ "PARSE_PKG")
  set(name_)
  set(names_)

  foreach(arg ${ARGN})
    if(state_ STREQUAL "PARSE_PKG")
      if(arg STREQUAL "PKG")
        set(state_ "PARSE_NAME")
        set(name_)
        set(names_)
      else()
        message(FATAL_ERROR "malformed pkg_find, "
                            "expected 'PKG' but got '${arg}'")
      endif()
    elseif(state_ STREQUAL "PARSE_NAME")
      set(name_ ${arg})
      set(state_ "PARSE_KEYWORD")
    elseif(state_ STREQUAL "PARSE_KEYWORD")
      if(arg STREQUAL "PKG")
        _pkg_query_loop(${name_} ${names_})
        set(name_)
        set(names_)
        set(state_ "PARSE_NAME")
      elseif(arg STREQUAL "NAMES")
        set(state_ "PARSE_NAMES")
      else()
        message(FATAL_ERROR "malformed pkg_find, expected keyword "
                            "'PKG' or 'NAMES' but got '${arg}'")
      endif()
    elseif(state_ STREQUAL "PARSE_NAMES")
      if(arg STREQUAL "PKG")
        _pkg_query_loop(${name_} ${names_})
        set(name_)
        set(names_)
        set(state_ "PARSE_NAME")
      elseif(arg STREQUAL "NAMES")
        message(FATAL_ERROR "malformed pkg_find, found literal "
                            "'NAMES' when expecting library names")
      else()
        list(APPEND names_ ${arg})
      endif()
    endif()
  endforeach()

  if(name_)
    _pkg_query_loop(${name_} ${names_})
  endif()
endfunction()

# Add flags to compile/link options for the target according to the output of
# pkg-config. Asserts that the given pkg-config packages were found
function(target_pkg_depends target pkg0)
  foreach(pkgname ${pkg0} ${ARGN})
    if(NOT PKG_${pkgname}_FOUND)
      message(FATAL_ERROR "pkg-config package ${pkgname} is not enumerated, but"
                          " required by ${target}")
    endif()
    if(NOT ${PKG_${pkgname}_FOUND})
      message(FATAL_ERROR "pkg-config package ${pkgname} is not found, but"
                          " required by ${target}")
    endif()
    if(PKG_${pkgname}_INCLUDEDIRS)
      # TODO(josh): passthrough things like SYSTEM, BEFORE,
      # INTERFACE|PUBLIC|PRIVATE
      target_include_directories(${target} SYSTEM
                                 PUBLIC ${PKG_${pkgname}_INCLUDEDIRS})
    endif()
    if(PKG_${pkgname}_CFLAGS)
      # TODO(josh): passthrough things like BEFORE, INTERFACE|PUBLIC|PRIVATE
      target_compile_options(${target} PUBLIC ${PKG_${pkgname}_CFLAGS})
    endif()
    if(PKG_${pkgname}_LIBDIRS)
      get_target_property(lflags_ ${target} LINK_FLAGS)
      if(lflags_)
        list(APPEND lflags_ ${PKG_${pkgname}_lflags})
        set_target_properties(${target} PROPERTIES LINK_FLAGS ${lflags_})
      else()
        set_target_properties(${target} PROPERTIES LINK_FLAGS
                                                   ${PKG_${pkgname}_lflags})
      endif()

    endif()
    if(PKG_${pkgname}_LIBS)
      # Passthrough options like INTERFACE|PUBLIC|PRIVATE and
      # debug|optimized|general
      target_link_libraries(${target} PUBLIC ${PKG_${pkgname}_LIBS})
    endif()
  endforeach()
endfunction()
