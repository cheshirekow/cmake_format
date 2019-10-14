format_and_lint(
  cmake_format
  # cmake-format: sort
  __init__.py
  __main__.py
  annotate.py
  commands.py
  command_tests/add_custom_command_tests.py
  command_tests/add_executable_tests.py
  command_tests/add_library_tests.py
  command_tests/conditional_tests.py
  command_tests/export_tests.py
  command_tests/file_tests.py
  command_tests/__init__.py
  command_tests/install_tests.py
  command_tests/__main__.py
  command_tests/misc_tests.py
  command_tests/set_tests.py
  common.py
  configuration.py
  doc/conf.py
  doc/gendoc_sources.py
  formatter.py
  invocation_tests.py
  layout_tests.py
  lexer.py
  lexer_tests.py
  markup.py
  markup_tests.py
  parse_funs/add_executable.py
  parse_funs/add_library.py
  parse_funs/add_xxx.py
  parse_funs/external_project.py
  parse_funs/fetch_content.py
  parse_funs/file.py
  parse_funs/__init__.py
  parse_funs/install.py
  parser.py
  parser_tests.py
  pypi/setup.py
  render.py
  screw_users_test.py
  test/cmake-format.py
  test/cmake-format-split-1.py
  test/cmake-format-split-2.py
  tests.py)

set(
  _testnames
  invocation_tests
  layout_tests
  lexer_tests
  markup_tests
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

add_subdirectory(doc)
add_subdirectory(command_tests)
