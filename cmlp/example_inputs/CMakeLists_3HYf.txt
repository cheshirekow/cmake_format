cmake_minimum_required(VERSION 2.8.3)
project(quux_user)
find_package(catkin REQUIRED)

catkin_package()
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

find_package(quux_msgs)
assert_unset(quux_msgs_INCLUDE_DIRS)

include_directories(${quux_msgs_INCLUDE_DIRS})

find_package(rostime)
include_directories(${rostime_INCLUDE_DIRS})
assert(rostime_INCLUDE_DIRS)
assert(rostime_LIBRARIES)

find_package(cpp_common)
include_directories(${cpp_common_INCLUDE_DIRS})

find_package(roscpp_traits)
include_directories(${roscpp_traits_INCLUDE_DIRS})

find_package(roscpp_serialization)
include_directories(${roscpp_serialization_INCLUDE_DIRS})
assert(roscpp_serialization_LIBRARIES)

find_package(sensor_msgs)
include_directories(${sensor_msgs_INCLUDE_DIRS})


include_directories(${std_msgs_INCLUDE_DIRS} ${quux_msgs_INCLUDE_DIRS})

add_executable(quux_user-exec src/main.cpp)
add_dependencies(quux_user-exec sensor_msgs_gencpp)

message(STATUS ${roscpp_serialization_LIBRARIES})

target_link_libraries(quux_user-exec ${roscpp_serialization_LIBRARIES} ${rostime_LIBRARIES})

add_executable(quux_srv-exec src/srv_test.cpp)

target_link_libraries(quux_srv-exec ${roscpp_serialization_LIBRARIES})
add_dependencies(quux_srv-exec sensor_msgs_gencpp)