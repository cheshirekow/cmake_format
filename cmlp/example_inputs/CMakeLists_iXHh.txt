cmake_minimum_required(VERSION 2.8)
project(a)
catkin_project(a
  INCLUDE_DIRS include
  LIBRARIES a
#  PYTHONPATH src
  )

find_package(catkin REQUIRED)

add_library(a SHARED lib.cpp)

add_message_files(
  DIRECTORY msg
  FILES AMsg.msg
)


# catkin_python_setup()
# enable_python(a)

generate_messages(DEPENDENCIES std_msgs)
