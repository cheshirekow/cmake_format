cmake_minimum_required(VERSION 2.4.6)

project(python-orocos-kdl)

set (ROS_ROOT $ENV{ROS_ROOT} )
if (ROS_ROOT)
  include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)
  rosbuild_init()
else()
  find_package(Orocos-KDL)
  include_directories(${Orocos-KDL_INCLUDE_DIRS})
  link_directories(${Orocos-KDL_LIBRARY_DIRS})
endif()

#set the default path for built executables to the "bin" directory
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
#set the default path for built libraries to the "lib" directory
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

#uncomment if you have defined messages
#rosbuild_genmsg()
#uncomment if you have defined services
#rosbuild_gensrv()

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
find_package(SIP REQUIRED)
include(SIPMacros)

include_directories(${SIP_INCLUDE_DIR} ${PYTHON_INCLUDE_DIRS})

file(GLOB SIP_FILES "${CMAKE_CURRENT_SOURCE_DIR}/*.sip")
set(SIP_INCLUDES ${SIP_FILES})
set(SIP_EXTRA_OPTIONS "-o")
set(PYTHON_PACKAGES_DIR_NAME "")
set(PYTHON_PACKAGES_DIR_NAME "dist-packages")
set(PYTHON_SITE_PACKAGES_INSTALL_DIR
${CMAKE_INSTALL_PREFIX}/lib${LIB_SUFFIX}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/${PYTHON_PACKAGES_DIR_NAME}
 CACHE PATH "The directory where python modules will be installed to.")
add_sip_python_module(PyKDL PyKDL/PyKDL.sip orocos-kdl)