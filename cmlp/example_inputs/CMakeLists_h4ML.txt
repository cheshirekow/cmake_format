cmake_minimum_required(VERSION 2.8)
project(c)
catkin_project(c
  INCLUDE_DIRS include
  LIBRARIES c-one c-two
  )

find_package(catkin REQUIRED)
find_package(a)
include_directories(${a_INCLUDE_DIRS})

add_library(c-one SHARED lib.cpp)
add_library(c-two SHARED lib.cpp)
target_link_libraries(c-one ${a_LIBRARIES})
target_link_libraries(c-two ${a_LIBRARIES})

add_message_files(
  DIRECTORY msg
  FILES CMsg.msg
)



# catkin_python_setup()
# enable_python(c)

# generate_messages(DEPENDENCIES std_msgs a)

