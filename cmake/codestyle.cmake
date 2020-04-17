# Create format and lint rules for a file manifest
#
# usage:
# ~~~
# format_and_lint(<slug>
#   <file-list>
#   [BZL <bzl-file-list>]
#   [CMAKE <cmake-file-list>]
#   [CC <cc-file-list>]
#   [JS <js-file-list>]
#   [PY <py-file-list>]
#   [SHELL <sh-file-list>])
# ~~~
#
# Will create rules `${slug}_lint` and `${slug}_format` using the standard code
# formatters and lint checkers for the appropriate language. These tools are:
#
# ~~~
# BZL:
#   formatter: buildifier
#
# CMAKE:
#   formatter: cmake-format
#    linter: cmake-lint
#
# CC:
#   formatter: clang-format
#   linter: cpplint, clang-tidy
#
# JS:
#   formatter: js-beautify
#   linter: eslint
#
# PY:
#   formatter: autopep8
#   linter: pylint, flake8
# ~~~
if(EXISTS ${CMAKE_SOURCE_DIR}/cmake_format)
  set(CMAKE_FORMAT_CMD python -Bm cmake_format)
  set(CMAKE_LINT_CMD python -Bm cmake_lint)
else()
  set(CMAKE_FORMAT_CMD cmake-format)
  set(CMAKE_LINT_CMD cmake-lint)
endif()

# Generate targets to format or lint the list of files
#
# Usage:
# ~~~
# format_and_lint(<slug>
#   [BZL filepath1 [filepath2 [...]]]
#   [CMAKE filepath1 [filepath2 [...]]]
#   [CC filepath1 [filepath2 [...]]]
#   [CCDEPENDS filepath1 [filepath2 [...]]]
#   [JS filepath1 [filepath2 [...]]]
#   [PY filepath1 [filepath2 [...]]]
#   [SHELL filepath1 [filepath2 [...]]]
# )
# ~~~
function(format_and_lint slug)
  set(_multiargs
      BZL
      CMAKE
      CC
      CCDEPENDS
      JS
      PY
      SHELL)
  cmake_parse_arguments(_args "" "" "${_multiargs}" ${ARGN})
  set(_unknown_files)
  foreach(_arg ${_args_UNPARSED_ARGUMENTS})
    if("${_arg}" MATCHES ".*\\.bzl$"
       OR "${_arg}" MATCHES "(.*/)?BUILD"
       OR "${_arg}" MATCHES "(.*/)?WORKSPACE")
      list(APPEND _args_BZL ${_arg})
    elseif("${_arg}" MATCHES ".*\\.cmake$" OR "${_arg}" MATCHES
                                              ".*CMakeLists.txt")
      list(APPEND _args_CMAKE ${_arg})
    elseif("${_arg}" MATCHES ".*\\.py$")
      list(APPEND _args_PY ${_arg})
    elseif("${_arg}" MATCHES ".*\\.(h|(hh)|(hpp))$")
      list(APPEND _args_CC ${_arg})
    elseif("${_arg}" MATCHES ".*\\.tcc$")
      list(APPEND _args_CC ${_arg})
    elseif("${_arg}" MATCHES ".*\\.(c|(cc)|(cpp))$")
      list(APPEND _args_CC ${_arg})
    elseif("${_arg}" MATCHES ".*\\.js(\\.tpl)?$")
      list(APPEND _args_JS ${_arg})
    elseif("${_arg}" MATCHES ".*\\.sh$")
      list(APPEND _args_SHELL ${_arg})
    else()
      list(APPEND _unknown_files ${_arg})
    endif()
  endforeach()

  # NOTE(josh): we create this dummy target which touches a dummy file that all
  # the rules below depend on. This gives us a synchronization point where we
  # can add dependencies and ensure these dependencies happen before any of the
  # rules below.
  set(lintdep_witness ${CMAKE_CURRENT_BINARY_DIR}/lint-${slug}-deps.witness)
  add_custom_target(
    lint-${slug}-deps
    COMMAND touch -a ${lintdep_witness}
    BYPRODUCTS ${lintdep_witness}
    COMMENT "Dependency fence for lint-${slug}")

  if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
    add_custom_command(
      OUTPUT ${lintdep_witness}
      COMMAND true
      DEPENDS lint-${slug}-deps
      COMMENT "Makefile stub for lint-${slug} dependency fence")
  endif()

  set(_bzl_lintdeps)
  set(_bzl_fmtdeps)
  set(_bzl_chkfmtdeps)
  foreach(_filename ${_args_BZL})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      COMMAND buildifier -indent 2 -mode check
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      DEPENDS ${_filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _bzl_lintdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      COMMAND buildifier -indent 2 -mode fix
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _bzl_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      COMMAND buildifier -indent 2 -mode check
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _bzl_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
  endforeach()

  set(_cmake_lintdeps)
  set(_cmake_fmtdeps)
  set(_cmake_chkfmtdeps)
  foreach(_filename ${_args_CMAKE})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      # COMMAND ${CMAKE_LINT_CMD} --suppress-decorations ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      DEPENDS ${_filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _cmake_lintdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      COMMAND ${CMAKE_FORMAT_CMD} -i ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _cmake_fmtdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      COMMAND ${CMAKE_FORMAT_CMD} --check
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _cmake_chkfmtdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
  endforeach()

  set(_cc_lintdeps)
  set(_cc_fmtdeps)
  set(_cc_chkfmtdeps)
  foreach(_filename ${_args_CC})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    if("${_filename}" MATCHES ".*\\.(c|(cc)|(cpp))$")
      # NOTE(josh): clang-tidy doesn't work on header files. It will check
      # headers that it finds in the inclusion of translation units it
      # understands
      add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.tidy
        COMMAND
          clang-tidy-8 -p ${CMAKE_BINARY_DIR} -header-filter=${CMAKE_SOURCE_DIR}
          ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
        COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
        COMMAND ${CMAKE_COMMAND} -E touch
                ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.tidy
        DEPENDS ${_filename} ${_args_CCDEPENDS} ${lintdep_witness}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
      list(APPEND _cc_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.tidy)
    endif()

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.cpplint
      COMMAND cpplint ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.cpplint
      DEPENDS ${_filename} ${_args_CCDEPENDS} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _cc_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.cpplint)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      COMMAND clang-format-8 -style file -i ${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      DEPENDS ${_filename} ${_args_CCDEPENDS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _cc_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      COMMAND
      COMMAND
        clang-format-8 -style file ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} "|"
        diff -u ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      DEPENDS ${_filename} ${_args_CCDEPENDS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _cc_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
  endforeach()

  set(_js_lintdeps)
  set(_js_fmtdeps)
  set(_js_chkfmtdeps)
  foreach(_filename ${_args_JS})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      COMMAND eslint ${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      DEPENDS ${_filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _js_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      COMMAND js-beautify -r ${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _js_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      COMMAND js-beautify ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} "|" diff -u
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _js_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
  endforeach()

  set(_py_lintdeps)
  set(_py_fmtdeps)
  set(_py_chkfmtdeps)
  foreach(_filename ${_args_PY})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
             # NOTE(josh): --rcfile= is required because some of our python
             # files are note entirely within the package tree from the root of
             # the repository. As such pylint will not match the rcfile in the
             # root of the repository.
      COMMAND
        env PYTHONPATH=${CMAKE_SOURCE_DIR} pylint
        --rcfile=${CMAKE_SOURCE_DIR}/pylintrc -sn -rn
        ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
        # NOTE(josh): flake8 tries to use semaphores which fail in our
        # containers https://bugs.python.org/issue3770 (probably due to
        # /proc/shmem or something not being mounted)
      COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} flake8 --jobs 1
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      DEPENDS ${_filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _py_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      COMMAND autopep8 -i ${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND _py_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      COMMAND autopep8 ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} "|" diff -u
              ${CMAKE_CURRENT_SOURCE_DIR}/${_filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
      DEPENDS ${_filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _py_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
  endforeach()

  set(_shell_lintdeps)
  set(_shell_fmtdeps)
  set(_shell_chkfmtdeps)
  foreach(_filename ${_args_SHELL})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${_filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      COMMAND shellcheck ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp
      DEPENDS ${_filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND _shell_lintdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.lintstamp)

    # NOTE(josh): beautysh is broken. It destroys shell scripts
    # ~~~
    # add_custom_command(
    #   OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
    #   COMMAND beautysh --indent-size=2 ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
    #   COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
    #   COMMAND ${CMAKE_COMMAND} -E touch
    #           ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp
    #   DEPENDS ${_filename}
    #   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    # list(APPEND _shell_fmtdeps
    #      ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.fmtstamp)
    #
    # add_custom_command(
    #   OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
    #   COMMAND beautysh --indent-size=2 --check
    #           ${CMAKE_CURRENT_SOURCE_DIR}/${_filename}
    #   COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
    #   COMMAND ${CMAKE_COMMAND} -E touch
    #           ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt
    #   DEPENDS ${_filename}
    #   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    # list(APPEND _shell_chkfmtdeps
    #      ${CMAKE_CURRENT_BINARY_DIR}/${_filename}.chkfmt)
    # ~~~
  endforeach()

  if(_unknown_files)
    string(REPLACE ";" "\n  " filelist_ "${_unknown_files}")
    message(
      WARNING "The following files will not be linted/formatted because their"
              " extension is not recognized: \n  ${filelist_}")
  endif()

  file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${slug}.lint-manifest "")
  foreach(listname_ _args_CC _args_CMAKE _args_JS _args_PY _args_SHELL)
    if(${listname_})
      string(REPLACE ";" "\n" filenames_ "${${listname_}}")
      file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${slug}.lint-manifest
           "${filenames_}\n")
    endif()
  endforeach()

  set(_slugs bzl cc cmake js py shell)
  add_custom_target(lint-${slug})
  add_dependencies(lint lint-${slug})
  foreach(_slug ${_slugs})
    if(_${_slug}_lintdeps)
      add_custom_target(lint-${_slug}-${slug} DEPENDS ${_${_slug}_lintdeps})
      add_dependencies(lint-${slug} lint-${_slug}-${slug})
    endif()
  endforeach()

  add_custom_target(format-${slug})
  add_dependencies(format format-${slug})
  foreach(_slug ${_slugs})
    if(_${_slug}_fmtdeps)
      add_custom_target(format-${_slug}-${slug} DEPENDS ${_${_slug}_fmtdeps})
      add_dependencies(format-${slug} format-${_slug}-${slug})
    endif()
  endforeach()

  add_custom_target(chkfmt-${slug})
  add_dependencies(chkfmt chkfmt-${slug})
  foreach(_slug ${_slugs})
    if(_${_slug}_chkfmtdeps)
      add_custom_target(chkfmt-${_slug}-${slug} DEPENDS ${_${_slug}_chkfmtdeps})
      add_dependencies(chkfmt-${slug} chkfmt-${_slug}-${slug})
    endif()
  endforeach()
endfunction()
