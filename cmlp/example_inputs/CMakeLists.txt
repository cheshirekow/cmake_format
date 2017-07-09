cmake_minimum_required(VERSION 2.4.6)
include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)
rosbuild_init()
rosbuild_make_distribution(1.6.0)

rosbuild_add_boost_directories()

#Plugins
rosbuild_add_library(mean src/mean.cpp)
rosbuild_add_library(params src/test_params.cpp)
rosbuild_add_library(increment src/increment.cpp)
rosbuild_add_library(median src/median.cpp)
rosbuild_add_library(transfer_function src/transfer_function.cpp)

# Test median filter
rosbuild_add_executable(median_test EXCLUDE_FROM_ALL test/test_median.cpp )
target_link_libraries(median_test median) 
rosbuild_add_gtest_build_flags(median_test)
rosbuild_add_rostest(test/test_median.launch)

#test transfer function filter
rosbuild_add_executable(transfer_function_test EXCLUDE_FROM_ALL test/test_transfer_function.cpp)
target_link_libraries(transfer_function_test transfer_function)
rosbuild_add_gtest_build_flags(transfer_function_test)
rosbuild_add_rostest(test/test_transfer_function.launch)

#test mean filter
rosbuild_add_executable(mean_test EXCLUDE_FROM_ALL test/test_mean.cpp)
target_link_libraries(mean_test mean)
rosbuild_add_gtest_build_flags(mean_test)
rosbuild_add_rostest(test/test_mean.launch)

#test params filter
rosbuild_add_executable(params_test EXCLUDE_FROM_ALL test/test_params.cpp)
target_link_libraries(params_test params)
rosbuild_add_gtest_build_flags(params_test)
rosbuild_add_rostest(test/test_params.launch)

#Test plugin loading into filter chain
rosbuild_add_executable(chain_test EXCLUDE_FROM_ALL test/test_chain.cpp)
rosbuild_add_gtest_build_flags(chain_test)
rosbuild_add_rostest(test/test_chain.launch)
rosbuild_link_boost(chain_test system) # Needed for OSX

# Test reltime safe buffer class
rosbuild_add_gtest(realtime_buffer_test EXCLUDE_FROM_ALL test/test_realtime_circular_buffer.cpp)
