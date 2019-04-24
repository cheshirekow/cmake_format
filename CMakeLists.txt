cmake_minimum_required(VERSION 3.5)
project(cheshirekow)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

include(${CMAKE_SOURCE_DIR}/cmake/codestyle.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/ctest_helpers.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/doctools.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/pkgconfig.cmake)

find_package(Threads REQUIRED)
pkg_find(PKG eigen3
         PKG fontconfig
         PKG freetype2
         PKG fuse
         PKG gnuradio-osmosdr
         PKG gnuradio-filter
         PKG libcurl
         PKG libglog
         PKG librtlsdr
         PKG libudev
         PKG vulkan
         PKG x11-xcb)

include_directories(${CMAKE_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/third_party/googletest/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/re2)
include_directories(${CMAKE_SOURCE_DIR}/third_party/fmt/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/glm)

set(CXX_STANDARD "c++11" CACHE STRING "argument to '-std=' for C++ compiler")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=${CXX_STANDARD}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -rdynamic")

add_custom_target(format)
add_custom_target(lint)

add_custom_target(doc)

set(ENV{PYTHONPATH} ${CMAKE_SOURCE_DIR})
set(CTEST_ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")

set_property(GLOBAL PROPERTY gloal_doc_files "")

# NOTE(josh): search through the list of child directories and add any that
# actually contain a listfile. While globs are evil, this is necessary for
# sparse checkouts. We can and should correctly add dependencies for this glob
# in order to retrigger cmake.
file(GLOB children RELATIVE ${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/*)
foreach(child ${children})
  if(EXISTS ${CMAKE_SOURCE_DIR}/${child}/CMakeLists.txt)
    message("Enabling subdirectory '${child}' for this checkout")
    add_subdirectory(${child})
  endif()
endforeach()

# NOTE(josh): some sparse checkouts don't include doxygen
if(EXISTS ${CMAKE_SOURCE_DIR}/doxy.config.in)
  # configure the doxygen configuration
  # NOTE(josh): maybe want to expose this for editor integration
  # ~~~
  # set(DOXY_WARN_FORMAT "\"$file($line) : $text \"")
  # set(DOXY_WARN_FORMAT "\"$file:$line: $text \"")
  # ~~~
  configure_file("${PROJECT_SOURCE_DIR}/doxy.config.in"
                "${PROJECT_BINARY_DIR}/doxy.config")

  add_custom_command(OUTPUT ${PROJECT_BINARY_DIR}/doxy.stamp
                    COMMAND doxygen ${PROJECT_BINARY_DIR}/doxy.config
                    COMMAND touch ${PROJECT_BINARY_DIR}/doxy.stamp
                    DEPENDS ${PROJECT_BINARY_DIR}/doxy.config
                    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(doxygen DEPENDS ${PROJECT_BINARY_DIR}/doxy.stamp)
  add_dependencies(doc doxygen)
endif()
