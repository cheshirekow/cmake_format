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
