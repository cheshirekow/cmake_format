format_and_lint(
  cmake_lint
  # cmake-format: sort
  __init__.py
  __main__.py
  basic_checker.py
  gendocs.py
  CMakeLists.txt
  lint_util.py
  lintdb.py
  test/__init__.py
  test/__main__.py
  test/execution_tests.py
  test/expect_tests.py
  test/genfiles.py
  #EXCLUDE "test/.*"
)

set(_genfiles ${CMAKE_CURRENT_SOURCE_DIR}/test/expect_lint.cmake
              ${CMAKE_CURRENT_SOURCE_DIR}/test/lint_tests.cmake)
add_custom_command(
  OUTPUT ${_genfiles}
  COMMAND python -Bm cmake_lint.test.genfiles
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_custom_target(cmake_lint-test-genfiles DEPENDS ${_genfiles})
add_dependencies(gen cmake_lint-test-genfiles)

foreach(_testcase TestFormatFiles ConfigTestCase LintTests)
  add_test(
    NAME cmake_lint-${_testcase}
    COMMAND python -Bm cmake_lint.test ${_testcase}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()
