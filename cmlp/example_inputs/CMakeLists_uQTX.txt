cmake_minimum_required(VERSION 2.8)
project(catkin_test)
find_package(catkin REQUIRED)

find_package(genmsg REQUIRED)
find_package(std_msgs REQUIRED)


foreach(subdir
    quux_msgs
    quux_user
    a
    b
    c
    d
    )
  add_subdirectory(${subdir})
endforeach()

