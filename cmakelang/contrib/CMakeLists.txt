tangent_addtest(
  NAME cmakelang-validate-pullrequest
  COMMAND python -Bm cmakelang.contrib.validate_pullrequest
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

tangent_addtest(
  NAME cmakelang-validate-database
  COMMAND python -Bm cmakelang.contrib.validate_database
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
