set(_testnames invocation_tests layout_tests lexer_tests markup_tests
               parser_tests)

foreach(testname ${_testnames})
  add_test(
    NAME cmake_format-${testname}
    COMMAND python -Bm cmake_format.${testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(testname ${_testnames})
    add_test(
      NAME cmake_format-${testname}_py3
      COMMAND python3 -Bm cmake_format.${testname}
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
  OUTPUT_VARIABLE _src_version
  OUTPUT_STRIP_TRAILING_WHITESPACE)
if(NOT _resultcode EQUAL 0)
  message(
    FATAL_ERROR "Failed to get cmake-format version number from __init__.py")
endif()

# NOTE(josh): python uses dot to separate pre-release while node uses dash
string(REGEX REPLACE "([0-9]+\\.[0-9]+\\.[0-9]+)\\.(.*)" "\\1-\\2"
                     _extension_version "${_src_version}")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/.egg
  COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/.egg
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_distdir ${CMAKE_CURRENT_BINARY_DIR}/dist)
add_custom_command(
  OUTPUT ${_distdir}/cmake_format-${_src_version}.tar.gz
         ${_distdir}/cmake_format-${_src_version}-py3-none-any.whl
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

add_custom_target(
  cmake_format-wheel
  DEPENDS ${_distdir}/cmake_format-${_src_version}-py3-none-any.whl)
add_dependencies(wheels cmake_format-wheel)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  COMMAND
    python -Bm tangent.tooling.get_release_notes
    cmake_format/doc/release_notes.rst \$\${TRAVIS_TAG} -o
    ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  DEPENDS doc/release_notes.rst
          ${CMAKE_SOURCE_DIR}/tangent/tooling/get_release_notes.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.md
  COMMAND
    pandoc -s -o ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.md
    ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_subdirectory(command_tests)
add_subdirectory(contrib)
add_subdirectory(doc)
add_subdirectory(test)
add_subdirectory(vscode_extension)

set(_vscedir ${CMAKE_CURRENT_BINARY_DIR}/vscode_extension)
add_custom_target(
  push-cmake_format-github-release
  COMMAND
    # cmake-format: off
    python -Bm tangent.tooling.github push-release
      --message ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.md
      cheshirekow/cmake_format \$\${TRAVIS_TAG}
      ${_distdir}/cmake_format-${_src_version}.tar.gz
      ${_distdir}/cmake_format-${_src_version}-py3-none-any.whl
      ${_vscedir}/cmake-format-${_extension_version}.vsix
    # cmake-format: on
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.md
          ${_distdir}/cmake_format-${_src_version}.tar.gz
          ${_distdir}/cmake_format-${_src_version}-py3-none-any.whl
          # ${_vscedir}/cmake-format-${_extension_version}.vsix
  COMMENT "Uploading release artifacts"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# NOTE(josh): cmake is broken. It fails to produce an accurate build system when
# we correctly specify the .vsix path in the above rule. We must use target
# level dependencies to get the correct order of operations and then omit the
# actual file-level dependency.
add_dependencies(push-cmake_format-github-release vscode-extension)
