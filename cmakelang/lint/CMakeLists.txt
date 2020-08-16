set(_genfiles ${CMAKE_CURRENT_SOURCE_DIR}/test/expect_lint.cmake
              ${CMAKE_CURRENT_SOURCE_DIR}/test/lint_tests.cmake)
add_custom_command(
  OUTPUT ${_genfiles}
  COMMAND python -Bm cmakelang.lint.test.genfiles
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_custom_target(cmakelang-lint-test-genfiles DEPENDS ${_genfiles})
add_dependencies(gen cmakelang-lint-test-genfiles)

foreach(testcase TestFormatFiles ConfigTestCase LintTests)
  tangent_addtest(
    NAME cmakelang-lint-${testcase}
    COMMAND python -Bm cmakelang.lint.test ${testcase}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()
