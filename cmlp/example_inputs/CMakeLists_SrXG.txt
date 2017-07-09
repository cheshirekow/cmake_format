cmake_minimum_required(VERSION 2.4.6)
include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)

# Set the build type.  Options are:
#  Coverage       : w/ debug symbols, w/o optimization, w/ code-coverage
#  Debug          : w/ debug symbols, w/o optimization
#  Release        : w/o debug symbols, w/ optimization
#  RelWithDebInfo : w/ debug symbols, w/ optimization
#  MinSizeRel     : w/o debug symbols, w/ optimization, stripped binaries
#set(ROS_BUILD_TYPE RelWithDebInfo)

rosbuild_init()

#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

#rosbuild_genmsg()
rosbuild_gensrv()

rosbuild_add_executable(test/exercise_bond test/exercise_bond.cpp)
rosbuild_add_gtest_build_flags(test/exercise_bond)
rosbuild_add_rostest(test/test_cpp.launch)

rosbuild_add_rostest(test/test_python.launch)

rosbuild_add_executable(test/test_callbacks_cpp test/test_callbacks_cpp.cpp)
rosbuild_add_gtest_build_flags(test/test_callbacks_cpp)
rosbuild_add_rostest(test/test_callbacks_cpp.launch)

rosbuild_add_rostest(test/test_callbacks_py.launch)

#common commands for building c++ executables and libraries
#rosbuild_add_library(${PROJECT_NAME} src/example.cpp)
#target_link_libraries(${PROJECT_NAME} another_library)
#rosbuild_add_boost_directories()
#rosbuild_link_boost(${PROJECT_NAME} thread)
#rosbuild_add_executable(example examples/example.cpp)
#target_link_libraries(example ${PROJECT_NAME})
