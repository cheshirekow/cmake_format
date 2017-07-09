cmake_minimum_required(VERSION 2.8)
project(quux_msgs)
catkin_project(${PROJECT_NAME})

 find_package(catkin REQUIRED)

find_package(genmsg REQUIRED)
find_package(std_msgs REQUIRED)

add_message_files(
  DIRECTORY msg
  FILES QuuxString.msg
)

generate_messages(DEPENDENCIES std_msgs)

