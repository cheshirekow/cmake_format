cmake_minimum_required(VERSION 2.8)
project(b)
catkin_project(b
  INCLUDE_DIRS include
  LIBRARIES b
  )

find_package(catkin REQUIRED)
find_package(a)
include_directories(${a_INCLUDE_DIRS})

add_library(b SHARED lib.cpp)
target_link_libraries(b ${a_LIBRARIES})

add_message_files(
  DIRECTORY msg
  FILES BMsg.msg
)



# catkin_python_setup()
# enable_python(b)

# generate_messages(DEPENDENCIES std_msgs)
