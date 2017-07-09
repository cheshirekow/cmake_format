cmake_minimum_required(VERSION 2.8.0)
project(smclib)

find_package(catkin REQUIRED)
catkin_package(INCLUDE_DIRS include)

catkin_python_setup()

# install the include folder
install(DIRECTORY include/${PROJECT_NAME}/
        DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
)
