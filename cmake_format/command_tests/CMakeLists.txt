set(MODPREFIX cmake_format.command_tests)

set(_testnames
    TestAddCustomCommand
    TestAddExecutableCommand
    TestAddLibraryCommand
    TestConditional
    TestExport
    TestFile
    TestForeach
    TestInstall
    TestMiscFormatting
    TestSetTargetProperties
    TestSet)

foreach(_testname ${_testnames})
  add_test(
    NAME cmake_format-${_testname}
    COMMAND python -Bm ${MODPREFIX} ${_testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(_testname ${_testnames})
    add_test(
      NAME cmake_format-${_testname}_py3
      COMMAND python3 -Bm ${MODPREFIX} ${_testname}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endforeach()
endif()
