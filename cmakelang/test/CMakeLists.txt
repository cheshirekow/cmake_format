tangent_addtest(
  NAME cmakelang-versionnumber-test
  COMMAND python -Bm cmakelang.test.version_number_test
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

tangent_addtest(
  NAME cmakelang-command-db-test
  COMMAND python -Bm cmakelang.test.command_db_test
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
