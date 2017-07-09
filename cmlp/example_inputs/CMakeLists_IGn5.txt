cmake_minimum_required(VERSION 2.8.0)
project(rospkg)
find_package(catkin)
catkin_stack()
catkin_project(rospkg
  )
catkin_python_setup()

install(FILES stack.yaml DESTINATION share/${PROJECT_NAME})

add_nosetests(${PROJECT_SOURCE_DIR})
