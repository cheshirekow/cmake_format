set(MODPREFIX cmakelang.command_tests)

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

foreach(testname ${_testnames})
  tangent_addtest(
    NAME cmakelang-${testname}
    COMMAND python -Bm ${MODPREFIX} ${testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(testname ${_testnames})
    tangent_addtest(
      NAME cmakelang-${testname}_py3
      COMMAND python3 -Bm ${MODPREFIX} ${testname}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endforeach()
endif()
