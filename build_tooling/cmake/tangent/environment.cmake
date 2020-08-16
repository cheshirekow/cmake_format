# Detect whether or not the source tree for this build is the upstream
# monorepository or a sparse export of it. Returns (via `<varname>`) the slug of
# the sparse export, if detected, or `NONE` if this is the monorepo.
#
# Usage:
# ~~~
# detect_sparse_export(<varname>)
# ~~~
function(detect_sparse_export varname)
  if("${TANGENT_BUILD_CONTEXT}" STREQUAL DEBIAN_PACKAGE)
    set(${varname}
        NONE
        PARENT_SCOPE)
    return()
  endif()

  if(EXISTS ${CMAKE_SOURCE_DIR}/.sparse-export)
    file(STRINGS ${CMAKE_SOURCE_DIR}/.sparse-export _sparse_export)
    set(${varname}
        "${_sparse_export}"
        PARENT_SCOPE)
    return()
  endif()

  set(exportsdir ${CMAKE_SOURCE_DIR}/tangent/tooling/sparse-exports/)
  if(EXISTS ${exportsdir}/iamgroot.txt)
    set(${varname}
        "groot"
        PARENT_SCOPE)
    return()
  endif()

  file(
    GLOB _children
    RELATIVE ${exportsdir}
    ${exportsdir}/*)
  list(LENGTH _children num_children)

  if("${num_children}" EQUAL 0)
    message(FATAL_ERROR " Invalid sparse export. ${exportsdir} is empty"
                        " and .sparse-export is  missing")
    return()
  endif()

  if("${num_children}" GREATER 1)
    string(REPLACE ";" "\n  " _children "${_children}")
    message(FATAL_ERROR " Invalid sparse export. ${exportsdir} contains"
                        " too many children:\n  ${_children}")
  endif()

  list(GET _children 0 this_export)
  set(${varname}
      ${this_export}
      PARENT_SCOPE)
endfunction()

# Detect the build environment that is running cmake. Returns in the calling
# scope the following variables:
#
# * IS_TRAVIS_CI - TRUE if this is on travis
# * IS_PULL_REQUEST - TRUE if this is a travis pull request build
# * TANGENT_IS_DEBIAN_BUILD - TRUE if this is a pbuilder/pbuild or launchpad
#   execution
# * TANGENT_SPARSE_EXPORT - set to the slug of the sparse export or `NONE` if
#   this is the monorepo
#
# Usage:
# ~~~
# include(environment.cmake)
# ~~~
set(IS_TRAVIS_CI FALSE)
if("$ENV{CI}" STREQUAL "true"
   AND "$ENV{TRAVIS}" STREQUAL "true")
  set(IS_TRAVIS_CI TRUE CACHE BOOL "This build is on travis" FORCE)
endif()

set(IS_PULL_REQUEST FALSE)
if(DEFINED ENV{TRAVIS_PULL_REQUEST} AND "$ENV{TRAVIS_PULL_REQUEST}" STREQUAL
                                        "true")
  set(IS_PULL_REQUEST TRUE)
endif()

set(TANGENT_IS_DEBIAN_BUILD FALSE)
if("${TANGENT_BUILD_CONTEXT}" STREQUAL DEBIAN_PACKAGE)
  set(TANGENT_IS_DEBIAN_BUILD TRUE)
endif()

detect_sparse_export(_sparse_export)
set(TANGENT_SPARSE_EXPORT "${_sparse_export}")

foreach(key ID RELEASE CODENAME DESCRIPTION)
  unset("BUILDENV_DISTRIB_${key}")
endforeach()
if(EXISTS "/etc/lsb-release")
  file(STRINGS "/etc/lsb-release" _lines)
  foreach(line ${_lines})
    if("${line}" MATCHES "^([^=]+)=(.+)")
      # cmake-lint: disable=C0103
      set("BUILDENV_${CMAKE_MATCH_1}" "${CMAKE_MATCH_2}")
      set_property(GLOBAL PROPERTY "BUILDENV_${CMAKE_MATCH_1}"
                                   "${CMAKE_MATCH_2}")
    endif()
  endforeach()
else()
  message(WARNING "Can't query lsb-release")
endif()

unset(BUILDENV_DPKG_ARCHITECTURE)
execute_process(
  COMMAND dpkg --print-architecture
  RESULT_VARIABLE _returncode
  OUTPUT_VARIABLE _this_arch
  ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE)
if(_returncode EQUAL 0)
  set(BUILDENV_DPKG_ARCHITECTURE "${_this_arch}")
  set_property(GLOBAL PROPERTY BUILDENV_DPKG_ARCHITECTURE "${_this_arch}")
else()
  message(WARNING "Failed to query current distribution architecture")
endif()
