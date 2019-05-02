set(MODPREFIX cmake_format.command_tests)

add_test(NAME cmake_format-add_custom_command_tests
         COMMAND python -m ${MODPREFIX}.add_custom_command_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-add_executable_tests
         COMMAND python -m ${MODPREFIX}.add_executable_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-add_library_tests
         COMMAND python -m ${MODPREFIX}.add_library_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-conditional_tests
         COMMAND python -m ${MODPREFIX}.conditional_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-export_tests
         COMMAND python -m ${MODPREFIX}.export_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-file_tests
         COMMAND python -m ${MODPREFIX}.file_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-install_tests
         COMMAND python -m ${MODPREFIX}.install_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-set_tests
         COMMAND python -m ${MODPREFIX}.set_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

if(NOT IS_TRAVIS_CI)
  add_test(NAME cmake_format-add_custom_command_tests_py3
           COMMAND python3 -m ${MODPREFIX}.add_custom_command_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-add_executable_tests_py3
           COMMAND python3 -m ${MODPREFIX}.add_executable_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-add_library_tests_py3
           COMMAND python3 -m ${MODPREFIX}.add_library_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-conditional_tests_py3
           COMMAND python3 -m ${MODPREFIX}.conditional_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-export_tests_py3
           COMMAND python3 -m ${MODPREFIX}.export_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-file_tests_py3
           COMMAND python3 -m ${MODPREFIX}.file_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-install_tests_py3
           COMMAND python3 -m ${MODPREFIX}.install_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-set_tests_py3
           COMMAND python3 -m ${MODPREFIX}.set_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()
