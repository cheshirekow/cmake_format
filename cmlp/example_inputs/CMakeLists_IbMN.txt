cmake_minimum_required(VERSION 2.8.0)
project(bondcpp)

find_package(catkin REQUIRED)

find_package(Boost REQUIRED)
find_package(catkin REQUIRED bond roscpp smclib)
catkin_package(DEPENDS bond Boost roscpp smclib
               INCLUDE_DIRS include
               LIBRARIES ${PROJECT_NAME}
)

include_directories(SYSTEM ${catkin_INCLUDE_DIRS}
                           ${BOOST_INCLUDE_DIRS}
)
include_directories(include)

add_library(${PROJECT_NAME}
  src/timeout.cpp
  src/bond.cpp
  src/BondSM_sm.cpp
)
target_link_libraries(${PROJECT_NAME} ${BOOST_LIBRARIES})

# install stuff
install(DIRECTORY include/${PROJECT_NAME}/
        DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
)
install(TARGETS ${PROJECT_NAME}
        DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
)
