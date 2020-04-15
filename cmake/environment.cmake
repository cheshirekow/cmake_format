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

  set(_exportsdir ${CMAKE_SOURCE_DIR}/tangent/tooling/sparse-exports/)
  if(EXISTS ${_exportsdir}/iamgroot.txt)
    set(${varname}
        "groot"
        PARENT_SCOPE)
    return()
  endif()

  file(
    GLOB _children
    RELATIVE ${_exportsdir}
    ${_exportsdir}/*)
  list(LENGTH _children _num_children)

  if("${_num_children}" EQUAL 0)
    message(FATAL_ERROR " Invalid sparse export. ${_exportsdir} is empty"
                        " and .sparse-export is  missing")
    return()
  endif()

  if("${_num_children}" GREATER 1)
    string(REPLACE ";" "\n  " "${_children}")
    message(FATAL_ERROR " Invalid sparse export. ${_exportsdir} contains"
                        " too many children:\n  ${_children}")
  endif()

  list(GET _children 0 _this_export)
  set(${varname}
      ${_this_export}
      PARENT_SCOPE)
endfunction()

function(detect_buildenv)
  set(IS_TRAVIS_CI FALSE)
  if(DEFINED ENV{CI}
     AND DEFINED ENV{TRAVIS}
     AND "$ENV{CI}" STREQUAL "true"
     AND "$ENV{TRAVIS}" STREQUAL "true")
    set(IS_TRAVIS_CI
        TRUE
        PARENT_SCOPE)
  endif()

  set(IS_PULL_REQUEST FALSE)
  if(DEFINED ENV{TRAVIS_PULL_REQUEST} AND "$ENV{TRAVIS_PULL_REQUEST}" STREQUAL
                                          "true")
    set(IS_PULL_REQUEST
        TRUE
        PARENT_SCOPE)
  endif()

  set(TANGENT_IS_DEBIAN_BUILD FALSE)
  if("${TANGENT_BUILD_CONTEXT}" STREQUAL DEBIAN_PACKAGE)
    set(TANGENT_IS_DEBIAN_BUILD TRUE)
  endif()

  detect_sparse_export(_sparse_export)
  set(TANGENT_SPARSE_EXPORT
      "${_sparse_export}"
      PARENT_SCOPE)
endfunction()
