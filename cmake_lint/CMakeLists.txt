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
  test/genfiles.py)

add_test(
  NAME cmake_lint-expect_tests
  COMMAND python -Bm cmake_lint.test
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_test(
  NAME cmake_lint-check-lint-manifest
  COMMAND
    python -Bm cmake.validate_lint_manifest #
    ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR} #
    --exclude "test/.*"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
