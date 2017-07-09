cmake_minimum_required(VERSION 2.8.3)

set(catkin_EXTRAS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

project(catkin)

if(NOT DEFINED CATKIN_TOPLEVEL)
  include(${catkin_EXTRAS_DIR}/all.cmake NO_POLICY_SCOPE)
endif()

catkin_package()

# for backward compatibility we provide ROSConfig(-version).cmake files
assert(CATKIN_BUILD_PREFIX)
file(COPY cmake/ROSConfig.cmake
  DESTINATION ${CATKIN_BUILD_PREFIX}/share/ros/cmake
)
assert(catkin_VERSION)
set(PROJECT_VERSION ${catkin_VERSION})
configure_file(${catkin_EXTRAS_DIR}/templates/pkgConfig-version.cmake.in
  ${CATKIN_BUILD_PREFIX}/share/ros/cmake/ROSConfig-version.cmake
  @ONLY
)
install(FILES ${CATKIN_BUILD_PREFIX}/share/ros/cmake/ROSConfig.cmake ${CATKIN_BUILD_PREFIX}/share/ros/cmake/ROSConfig-version.cmake
  DESTINATION share/ros/cmake
)

# for convenience we provide eigen-config(-version).cmake files
file(COPY cmake/Modules/eigen-config.cmake cmake/Modules/eigen-config-version.cmake
  DESTINATION ${CATKIN_BUILD_PREFIX}/share/eigen/cmake
)
install(FILES cmake/Modules/eigen-config.cmake cmake/Modules/eigen-config-version.cmake
  DESTINATION share/eigen/cmake
)

# install catkin scripts
add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/bin)

# install cmake files for catkin (except some files only used at build time of catkin)
install(DIRECTORY cmake
  DESTINATION share/catkin
  USE_SOURCE_PERMISSIONS
  PATTERN "catkinConfig.cmake.in" EXCLUDE
  PATTERN "Modules" EXCLUDE
  PATTERN "ROSConfig.cmake" EXCLUDE)

catkin_python_setup()

#catkin_add_nosetests(test)
