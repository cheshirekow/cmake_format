format_and_lint(
  cmake_format
  # cmake-format: sort
  CMakeLists.txt
  __init__.py
  __main__.py
  annotate.py
  commands.py
  command_tests/__init__.py
  command_tests/__main__.py
  command_tests/add_custom_command_tests.cmake
  command_tests/add_executable_tests.py
  command_tests/add_library_tests.py
  command_tests/CMakeLists.txt
  command_tests/misc_tests.py
  common.py
  config_util.py
  configuration.py
  contrib/__init__.py
  contrib/CMakeLists.txt
  contrib/sign_ca.py
  contrib/validate_database.py
  contrib/validate_pullrequest.py
  ctest_to.py
  doc/__init__.py
  doc/bits/dump-example.cmake
  doc/CMakeLists.txt
  doc/conf.py
  doc/gendoc.py
  formatter.py
  genparsers.py
  invocation_tests.py
  layout_tests.py
  lexer.py
  lexer_tests.py
  markup.py
  markup_tests.py
  parse/__init__.py
  parse/additional_nodes.py
  parse/argument_nodes.py
  parse/body_nodes.py
  parse/common.py
  parse/printer.py
  parse/properties.py
  parse/simple_nodes.py
  parse/statement_node.py
  parse/util.py
  parse/variables.py
  parse_funs/__init__.py
  parse_funs/add_executable.py
  parse_funs/add_library.py
  parse_funs/add_xxx.py
  parse_funs/break.py
  parse_funs/deprecated.py
  parse_funs/external_project.py
  parse_funs/fetch_content.py
  parse_funs/file.py
  parse_funs/foreach.py
  parse_funs/install.py
  parse_funs/list.py
  parse_funs/miscellaneous.py
  parse_funs/random.py
  parse_funs/set.py
  parse_funs/set_target_properties.py
  parser_tests.py
  pypi/setup.py
  render.py
  test/__init__.py
  test/cmake-format.py
  test/cmake-format-split-1.py
  test/cmake-format-split-2.py
  test/screw_users_test.py
  test/version_number_test.py
  tests.py
  tools/__init__.py
  tools/bump_version.py
  tools/create_pseudorelease_tag.py
  tools/gen_config_details.py
  tools/gen_rtd_requirements.py
  tools/generate_missing_parsers.py
  tools/get_release_notes.py
  tools/parse_cmake_help.py
  tools/push_github_release.py
  tools/usage_lexer.py
  tools/usage_parser.py
  tools/split_help.py
  vscode_extension/CMakeLists.txt
  EXCLUDE "command_tests/" "doc/stage" "test/.*" ".*\\.jinja.py$")

set(_testnames invocation_tests layout_tests lexer_tests markup_tests
               parser_tests)

foreach(_testname ${_testnames})
  add_test(
    NAME cmake_format-${_testname}
    COMMAND python -Bm cmake_format.${_testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(_testname ${_testnames})
    add_test(
      NAME cmake_format-${_testname}_py3
      COMMAND python3 -Bm cmake_format.${_testname}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endforeach()
endif()

set(_genfiles)
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/parse/variables.py
  COMMAND python -Bm cmake_format.tools.parse_cmake_help --outfile
          cmake_format/parse/variables.py variables
  DEPENDS tools/parse_cmake_help.py tools/variables.jinja.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Generating variables.py")
list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/parse/variables.py)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/parse/properties.py
  COMMAND python -Bm cmake_format.tools.parse_cmake_help --outfile
          cmake_format/parse/properties.py properties
  DEPENDS tools/parse_cmake_help.py tools/properties.jinja.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Generating properties.py")
list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/parse/properties.py)

add_custom_target(gen-cmake_format DEPENDS ${_genfiles})
add_dependencies(gen gen-cmake_format)

# NOTE(josh): this is just here to induce a dependency on the configure step. If
# we change the version number in __init__.py we need to re-run cmake so we can
# get out the version number and create rules for the distribution files.
configure_file(__init__.py init.stamp COPYONLY)

execute_process(
  COMMAND python -Bm cmake_format --version
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  RESULT_VARIABLE _resultcode
  OUTPUT_VARIABLE _version
  OUTPUT_STRIP_TRAILING_WHITESPACE)
if(NOT _resultcode EQUAL 0)
  message(
    FATAL_ERROR "Failed to get cmake-format version number from __init__.py")
endif()

# NOTE(josh): python uses dot to separate pre-release while node uses dash
string(REGEX REPLACE "([0-9]+\\.[0-9]+\\.[0-9]+)\\.(.*)" "\\1-\\2"
                     _extension_version "${_version}")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/.egg
  COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/.egg
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_distdir ${CMAKE_CURRENT_BINARY_DIR}/dist)
add_custom_command(
  OUTPUT ${_distdir}/cmake_format-${_version}.tar.gz
         ${_distdir}/cmake_format-${_version}-py3-none-any.whl
  COMMAND
    # cmake-format: off
    python cmake_format/pypi/setup.py
    build --build-base ${CMAKE_CURRENT_BINARY_DIR}
    egg_info --egg-base ${CMAKE_CURRENT_BINARY_DIR}/.egg
    bdist_wheel
      --bdist-dir ${CMAKE_CURRENT_BINARY_DIR}/bdist
      --dist-dir ${_distdir}
    sdist --dist-dir ${_distdir}
    # cmake-format: on
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/.egg
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(cmake_format-wheel
                  DEPENDS ${_distdir}/cmake_format-${_version}-py3-none-any.whl)
add_dependencies(wheels cmake_format-wheel)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.rst
  COMMAND
    python -Bm cmake_format.tools.get_release_notes
    cmake_format/doc/release_notes.rst \$\${TRAVIS_TAG} -o
    ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.rst
  DEPENDS doc/release_notes.rst tools/get_release_notes.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
  COMMAND pandoc -s -o ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
          ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.rst
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.rst
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_subdirectory(command_tests)
add_subdirectory(contrib)
add_subdirectory(doc)
add_subdirectory(test)
add_subdirectory(vscode_extension)

set(_vscedir ${CMAKE_CURRENT_BINARY_DIR}/vscode_extension)
add_custom_target(
  push-github-release
  COMMAND
    # cmake-format: off
    python -Bm cmake_format.tools.push_github_release
      --message ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
      \$\${TRAVIS_TAG}
      ${_distdir}/cmake_format-${_version}.tar.gz
      ${_distdir}/cmake_format-${_version}-py3-none-any.whl
      ${_vscedir}/cmake-format-${_extension_version}.vsix
    # cmake-format: on
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
          ${_distdir}/cmake_format-${_version}.tar.gz
          ${_distdir}/cmake_format-${_version}-py3-none-any.whl
          # ${_vscedir}/cmake-format-${_extension_version}.vsix
  COMMENT "Uploading release artifacts"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# NOTE(josh): cmake is broken. It fails to produce an accurate build system when
# we correctly specify the .vsix path in the above rule. We must use target
# level dependencies to get the correct order of operations and then omit the
# actual file-level dependency.
add_dependencies(push-github-release vscode-extension)
