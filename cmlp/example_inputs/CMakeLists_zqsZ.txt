cmake_minimum_required(VERSION 2.8.0)
project(bond)

find_package(catkin REQUIRED)
catkin_package()

find_package(catkin REQUIRED genmsg std_msgs)

add_message_files(DIRECTORY msg
                  FILES Constants.msg
                        Status.msg
)

generate_messages(DEPENDENCIES std_msgs)
