cmake_minimum_required(VERSION 3.5)
project(cheshirekow)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

include(${CMAKE_SOURCE_DIR}/cmake/codestyle.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/doctools.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/pkgconfig.cmake)

find_package(Threads REQUIRED)
pkg_find(PKG libcurl #
         PKG libglog
         PKG libudev
         PKG fuse
         PKG vulkan
         PKG x11-xcb)

include_directories(${CMAKE_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/third_party/googletest/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/re2)
include_directories(${CMAKE_SOURCE_DIR}/third_party/fmt/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/glm)

set(CXX_STANDARD_FLAG "-std=c++11"
    CACHE STRING "cxx command line flag specifying which C++ standard to apply")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_STANDARD_FLAG}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -rdynamic")

add_custom_target(format)
add_custom_target(lint)
add_custom_target(doc)

set(ENV{PYTHONPATH} ${CMAKE_SOURCE_DIR})
set(CTEST_ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")

set_property(GLOBAL PROPERTY gloal_doc_files "")

# NOTE(josh): don't add subdirectory for projects which aren't part of this
# sparse checkout
file(GLOB children RELATIVE ${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/*)
foreach(child ${children})
  if(EXISTS ${CMAKE_SOURCE_DIR}/${child}/CMakeLists.txt)
    message("Enabling subdirectory '${child}' for this checkout")
    add_subdirectory(${child})
  else()
    message("Skipping subdirectory '${child}' for this checkout")
  endif()
endforeach()
