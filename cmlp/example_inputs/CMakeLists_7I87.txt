cmake_minimum_required(VERSION 2.8.3)
project(a)
find_package(catkin REQUIRED COMPONENTS genmsg std_msgs)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES a
#  PYTHONPATH src
  )

add_library(a SHARED lib.cpp)

add_message_files(
  DIRECTORY msg
  FILES AMsg.msg
)


# catkin_python_setup()
# enable_python(a)

generate_messages(DEPENDENCIES std_msgs)
