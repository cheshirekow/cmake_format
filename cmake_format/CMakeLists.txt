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
  doc/CMakeLists.txt
  doc/conf.py
  doc/docsources_test.py
  doc/gendoc_sources.py
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
  parse/simple_nodes.py
  parse/statement_node.py
  parse/util.py
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
  tools/generate_missing_parsers.py
  tools/parse_cmake_help.py
  tools/usage_lexer.py
  tools/usage_parser.py)

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

add_subdirectory(command_tests)
add_subdirectory(contrib)
add_subdirectory(doc)
add_subdirectory(test)

add_test(
  NAME cmake_format-check-lint-manifest
  COMMAND
    python -Bm cmake.validate_lint_manifest #
    ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR} #
    --exclude "command_tests/" "test/.*" ".*\\.jinja.py$"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
