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
  # cmake-lint: disable=R0912,R0915
  set(multiargs
      BZL
      CMAKE
      CC
      CCDEPENDS
      JS
      PY
      SHELL)
  cmake_parse_arguments(_args "" "" "${multiargs}" ${ARGN})
  set(unknown_files)
  foreach(arg ${_args_UNPARSED_ARGUMENTS})
    if("${arg}" MATCHES ".*\\.bzl$"
       OR "${arg}" MATCHES "(.*/)?BUILD"
       OR "${arg}" MATCHES "(.*/)?WORKSPACE")
      list(APPEND _args_BZL ${arg})
    elseif("${arg}" MATCHES ".*\\.cmake$" OR "${arg}" MATCHES
                                             ".*CMakeLists.txt")
      list(APPEND _args_CMAKE ${arg})
    elseif("${arg}" MATCHES ".*\\.py$")
      list(APPEND _args_PY ${arg})
    elseif("${arg}" MATCHES ".*\\.(h|(hh)|(hpp))$")
      list(APPEND _args_CC ${arg})
    elseif("${arg}" MATCHES ".*\\.tcc$")
      list(APPEND _args_CC ${arg})
    elseif("${arg}" MATCHES ".*\\.(c|(cc)|(cpp))$")
      list(APPEND _args_CC ${arg})
    elseif("${arg}" MATCHES ".*\\.js(\\.tpl)?$")
      list(APPEND _args_JS ${arg})
    elseif("${arg}" MATCHES ".*\\.sh$")
      list(APPEND _args_SHELL ${arg})
    else()
      list(APPEND unknown_files ${arg})
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

  set(bzl_lintdeps)
  set(bzl_fmtdeps)
  set(bzl_chkfmtdeps)
  foreach(filename ${_args_BZL})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      COMMAND buildifier -indent 2 -mode check
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      DEPENDS ${filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND bzl_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      COMMAND buildifier -indent 2 -mode fix
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND bzl_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      COMMAND buildifier -indent 2 -mode check
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND bzl_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
  endforeach()

  set(cmake_lintdeps)
  set(cmake_fmtdeps)
  set(cmake_chkfmtdeps)
  foreach(filename ${_args_CMAKE})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      COMMAND ${CMAKE_LINT_CMD} --suppress-decorations ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      DEPENDS ${filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND cmake_lintdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      COMMAND ${CMAKE_FORMAT_CMD} -i ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND cmake_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      COMMAND ${CMAKE_FORMAT_CMD} --check
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND cmake_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
  endforeach()

  set(cc_lintdeps)
  set(cc_fmtdeps)
  set(cc_chkfmtdeps)
  foreach(filename ${_args_CC})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    if("${filename}" MATCHES ".*\\.(c|(cc)|(cpp))$")
      # NOTE(josh): clang-tidy doesn't work on header files. It will check
      # headers that it finds in the inclusion of translation units it
      # understands
      add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.tidy
        COMMAND
          clang-tidy-8 -p ${CMAKE_BINARY_DIR} -header-filter=${CMAKE_SOURCE_DIR}
          ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
        COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
        COMMAND ${CMAKE_COMMAND} -E touch
                ${CMAKE_CURRENT_BINARY_DIR}/${filename}.tidy
        DEPENDS ${filename} ${_args_CCDEPENDS} ${lintdep_witness}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
      list(APPEND cc_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.tidy)
    endif()

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.cpplint
      COMMAND cpplint ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.cpplint
      DEPENDS ${filename} ${_args_CCDEPENDS} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND cc_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.cpplint)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      COMMAND clang-format-8 -style file -i ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      DEPENDS ${filename} ${_args_CCDEPENDS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND cc_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      COMMAND
      COMMAND clang-format-8 -style file ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
              "|" diff -u ${CMAKE_CURRENT_SOURCE_DIR}/${filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      DEPENDS ${filename} ${_args_CCDEPENDS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND cc_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
  endforeach()

  set(js_lintdeps)
  set(js_fmtdeps)
  set(js_chkfmtdeps)
  foreach(filename ${_args_JS})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      COMMAND eslint ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      DEPENDS ${filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND js_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      COMMAND js-beautify -r ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND js_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      COMMAND js-beautify ${CMAKE_CURRENT_SOURCE_DIR}/${filename} "|" diff -u
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND js_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
  endforeach()

  set(py_lintdeps)
  set(py_fmtdeps)
  set(py_chkfmtdeps)
  foreach(filename ${_args_PY})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
             # NOTE(josh): --rcfile= is required because some of our python
             # files are note entirely within the package tree from the root of
             # the repository. As such pylint will not match the rcfile in the
             # root of the repository.
      COMMAND
        env PYTHONPATH=${CMAKE_SOURCE_DIR} pylint
        --rcfile=${CMAKE_SOURCE_DIR}/pylintrc -sn -rn
        ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
        # NOTE(josh): flake8 tries to use semaphores which fail in our
        # containers https://bugs.python.org/issue3770 (probably due to
        # /proc/shmem or something not being mounted)
      COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} flake8 --jobs 1
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND py_lintdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      COMMAND autopep8 -i ${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    list(APPEND py_fmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      COMMAND autopep8 ${CMAKE_CURRENT_SOURCE_DIR}/${filename} "|" diff -u
              ${CMAKE_CURRENT_SOURCE_DIR}/${filename} -
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
      DEPENDS ${filename}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND py_chkfmtdeps ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
  endforeach()

  set(shell_lintdeps)
  set(shell_fmtdeps)
  set(shell_chkfmtdeps)
  foreach(filename ${_args_SHELL})
    get_filename_component(_dirpath ${CMAKE_CURRENT_BINARY_DIR}/${filename}
                           DIRECTORY)

    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      COMMAND shellcheck ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
      COMMAND ${CMAKE_COMMAND} -E touch
              ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp
      DEPENDS ${filename} ${lintdep_witness}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    list(APPEND shell_lintdeps
         ${CMAKE_CURRENT_BINARY_DIR}/${filename}.lintstamp)

    # NOTE(josh): beautysh is broken. It destroys shell scripts
    # ~~~
    # add_custom_command(
    #   OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
    #   COMMAND beautysh --indent-size=2 ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
    #   COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
    #   COMMAND ${CMAKE_COMMAND} -E touch
    #           ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp
    #   DEPENDS ${filename}
    #   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    # list(APPEND shell_fmtdeps
    #      ${CMAKE_CURRENT_BINARY_DIR}/${filename}.fmtstamp)
    #
    # add_custom_command(
    #   OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
    #   COMMAND beautysh --indent-size=2 --check
    #           ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
    #   COMMAND ${CMAKE_COMMAND} -E make_directory ${_dirpath}
    #   COMMAND ${CMAKE_COMMAND} -E touch
    #           ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt
    #   DEPENDS ${filename}
    #   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    # list(APPEND shell_chkfmtdeps
    #      ${CMAKE_CURRENT_BINARY_DIR}/${filename}.chkfmt)
    # ~~~
  endforeach()

  if(unknown_files)
    string(REPLACE ";" "\n  " filelist "${unknown_files}")
    message(
      WARNING "The following files will not be linted/formatted because their"
              " extension is not recognized: \n  ${filelist}")
  endif()

  file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${slug}.lint-manifest "")
  foreach(listname _args_CC _args_CMAKE _args_JS _args_PY _args_SHELL)
    if(${listname})
      string(REPLACE ";" "\n" filenames "${${listname}}")
      file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${slug}.lint-manifest
           "${filenames}\n")
    endif()
  endforeach()

  set(langslugs bzl cc cmake js py shell)
  add_custom_target(lint-${slug})
  add_dependencies(lint lint-${slug})
  foreach(langslug ${langslugs})
    if(${langslug}_lintdeps)
      add_custom_target(lint-${langslug}-${slug}
                        DEPENDS ${${langslug}_lintdeps})
      add_dependencies(lint-${slug} lint-${langslug}-${slug})
    endif()
  endforeach()

  add_custom_target(format-${slug})
  add_dependencies(format format-${slug})
  foreach(langslug ${langslugs})
    if(${langslug}_fmtdeps)
      add_custom_target(format-${langslug}-${slug}
                        DEPENDS ${${langslug}_fmtdeps})
      add_dependencies(format-${slug} format-${langslug}-${slug})
    endif()
  endforeach()

  add_custom_target(chkfmt-${slug})
  add_dependencies(chkfmt chkfmt-${slug})
  foreach(langslug ${langslugs})
    if(${langslug}_chkfmtdeps)
      add_custom_target(chkfmt-${langslug}-${slug}
                        DEPENDS ${${langslug}_chkfmtdeps})
      add_dependencies(chkfmt-${slug} chkfmt-${langslug}-${slug})
    endif()
  endforeach()
endfunction()
