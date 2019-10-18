add_test(NAME cmake_format-versionnumber-test
         COMMAND python -B version_number_test.py
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
