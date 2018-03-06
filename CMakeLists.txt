cmake_minimum_required(VERSION 3.5)
project(cheshirekow)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

find_package(Threads REQUIRED)

include_directories(${CMAKE_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/third_party/googletest/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/re2)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -rdynamic")

add_custom_target(format ALL)
add_custom_target(lint ALL)
add_custom_target(doc ALL)

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
  endif()
endforeach()
