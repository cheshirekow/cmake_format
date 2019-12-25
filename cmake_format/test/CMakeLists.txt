add_test(NAME cmake_format-versionnumber-test
         COMMAND python -Bm cmake_format.test.version_number_test
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_test(NAME cmake_format-command-db-test
         COMMAND python -Bm cmake_format.test.command_db_test
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
