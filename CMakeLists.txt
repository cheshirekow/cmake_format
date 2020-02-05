cmake_minimum_required(VERSION 3.5)
project(cheshirekow)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

include(${CMAKE_SOURCE_DIR}/cmake/environment.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/codestyle.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/ctest_helpers.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/doctools.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/pkgconfig.cmake)

detect_buildenv()
find_package(Threads REQUIRED)
pkg_find(
  PKG eigen3
  PKG fontconfig
  PKG freetype2
  PKG fuse
  PKG glib-2.0
  PKG gnuradio-osmosdr
  PKG gnuradio-filter
  PKG gtk+-3.0
  PKG gtkmm-3.0
  PKG libcurl
  PKG libglog
  PKG libpng NAMES libpng12 libpng16
  PKG librtlsdr
  PKG libudev
  PKG tinyxml2
  PKG vulkan
  PKG x11-xcb)

include_directories(${CMAKE_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/third_party/googletest/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/re2)
include_directories(${CMAKE_SOURCE_DIR}/third_party/fmt/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/glm)

set(CXX_STANDARD
    "c++11"
    CACHE STRING "argument to '-std=' for C++ compiler")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=${CXX_STANDARD}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -rdynamic")

add_custom_target(doc)
add_custom_target(format)
add_custom_target(gen)
add_custom_target(lint)
add_custom_target(test-deps)
add_custom_target(wheels)

set(ENV{PYTHONPATH} ${CMAKE_SOURCE_DIR})
set(CTEST_ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")

# Will be populated by subdirectory listfiles with the dependencies of the
# master sphinx build
set_property(GLOBAL PROPERTY global_doc_files "")

# NOTE(josh): search through the list of child directories and add any that
# actually contain a listfile. While globs are evil, this is necessary for
# sparse checkouts. We can and should correctly add dependencies for this glob
# in order to retrigger cmake.
file(
  GLOB children
  RELATIVE ${CMAKE_SOURCE_DIR}
  ${CMAKE_SOURCE_DIR}/*)
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

  add_custom_command(
    OUTPUT ${PROJECT_BINARY_DIR}/doxy.stamp
    COMMAND doxygen ${PROJECT_BINARY_DIR}/doxy.config
    COMMAND touch ${PROJECT_BINARY_DIR}/doxy.stamp
    DEPENDS ${PROJECT_BINARY_DIR}/doxy.config
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(doxygen DEPENDS ${PROJECT_BINARY_DIR}/doxy.stamp)
  add_dependencies(doc doxygen)
endif()

# Validate sparse or update sparse export
add_custom_target(
  update-export
  COMMAND python -Bm tangent.tooling.export_sparse_subrepo update
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Updataing sparse export")

add_test(
  NAME verify-export
  COMMAND python -Bm tangent.tooling.export_sparse_subrepo update
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(
  better-test
  DEPENDS test-deps
  COMMAND ctest --force-new-ctest-process --output-on-failure
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMENT "Execute ctest")

add_custom_target(
  buildbot-test
  DEPENDS test-deps
  COMMAND ctest
    # cmake-format: off
    --label-exclude CI_DISABLED
    --force-new-ctest-process
    --output-on-failure
    --output-log ${CMAKE_BINARY_DIR}/ctestlog.txt
    # cmake-format: on
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_custom_target(pre-push)
add_dependencies(pre-push better-test doc format gen lint)
