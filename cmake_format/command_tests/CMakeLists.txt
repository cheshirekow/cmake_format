set(MODPREFIX cmake_format.command_tests)

set(
  _testnames
  add_custom_command_tests
  add_executable_tests
  add_library_tests
  conditional_tests
  export_tests
  file_tests
  install_tests
  misc_tests
  set_tests
)

foreach(_testname ${_testnames})
  add_test(
    NAME cmake_format-${_testname}
    COMMAND python -Bm ${MODPREFIX}.${_testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(_testname ${_testnames})
    add_test(
      NAME cmake_format-${_testname}_py3
      COMMAND python -Bm ${MODPREFIX}.${_testname}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endforeach()
endif()
