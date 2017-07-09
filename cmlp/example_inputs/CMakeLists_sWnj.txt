cmake_minimum_required(VERSION 2.8.3)
project(rosout)
find_package(catkin REQUIRED COMPONENTS roscpp)

catkin_package()

include_directories(${catkin_INCLUDE_DIRS})

find_package(Log4cxx QUIET)
if(NOT LOG4CXX_LIBRARIES)
  # backup plan, hope it is in the system path
  find_library(LOG4CXX_LIBRARIES log4cxx)
endif()
if(NOT LOG4CXX_LIBRARIES)
  message(FATAL_ERROR "Couldn't find log4cxx library")
endif()

add_executable(rosout rosout.cpp)
target_link_libraries(rosout ${catkin_LIBRARIES} ${LOG4CXX_LIBRARIES})

install(TARGETS rosout
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
