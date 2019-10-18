add_test(
  NAME cmake_format-validate-pullrequest
  COMMAND python -Bm cmake_format.contrib.validate_pullrequest
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_test(
  NAME cmake_format-validate-database
  COMMAND python -Bm cmake_format.contrib.validate_database
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
