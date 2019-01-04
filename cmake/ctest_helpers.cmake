# Add a target test.<test_name> which depends on the program of the same name,
# allows us to use the build system to run a test and build all it's
# dependencies
function(add_test_target test_name)
  add_custom_target(test.${test_name}
                    COMMAND ${test_name}
                    DEPENDS ${test_name}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
endfunction()
