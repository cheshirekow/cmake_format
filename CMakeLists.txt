cmake_minimum_required(VERSION 3.5)
project(tangentsky)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX
      ${CMAKE_BINARY_DIR}/install
      CACHE PATH "cmake installation directory")
endif()

include(CMakePackageConfigHelpers)
include(GNUInstallDirs)

find_package(Threads REQUIRED)
find_package(fmt QUIET)
find_package(Clang QUIET CONFIG)

if(EXISTS ${CMAKE_SOURCE_DIR}/build_tooling/cmake)
  list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/build_tooling/cmake)
endif()
# NOTE(josh): kitware documentation says that this is already the case, however
# that does not seem to be true.
list(APPEND CMAKE_MODULE_PATH /usr/share/cmake/Modules)
include(tangent)

# cmake-lint: disable=E1122
pkg_find(
  PKG cairomm-1.0
  PKG cairomm-svg-1.0
  PKG cairomm-pdf-1.0
  PKG eigen3
  PKG fontconfig
  PKG freetype2
  PKG fuse
  PKG gdk-pixbuf-2.0
  PKG gdkmm-3.0
  PKG glib-2.0
  PKG glibmm-2.4
  PKG gnuradio-osmosdr
  PKG gnuradio-filter
  PKG gobject-introspection-1.0
  PKG gtk+-3.0
  PKG gtkmm-3.0
  PKG libcurl
  PKG libelf
  PKG libglog
  PKG libpng NAMES libpng12 libpng16
  PKG librsvg-2.0
  PKG librtlsdr
  PKG libssh
  PKG libssh_threads
  PKG libudev
  PKG libzip
  PKG openssl
  PKG pango
  PKG pangoft2
  PKG pangomm-1.4
  PKG protobuf
  PKG tinyxml2
  PKG uuid
  PKG vulkan
  PKG x11-xcb)

include_directories(${CMAKE_SOURCE_DIR})

set(CMAKE_CXX_STANDARD "11")
set(CMAKE_C_STANDARD "99")
# NOTE(josh): needed to workaround some issue. I forgot what exactly.
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -rdynamic")

# Allow us to import/execute modules directly from the source tree
set(ENV{PYTHONPATH} ${CMAKE_SOURCE_DIR})
set(CTEST_ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")

add_compile_options(-Wall -Werror)

if(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
  if(CMAKE_CXX_COMPILE_VERSION VERSION_GREATER 5.9.99)
    add_compile_options(
      -Wimplicit-fallthrough
      "--system-header-prefix=${CMAKE_SOURCE_DIR}/third_party")
  endif()
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  if(CMAKE_CXX_COMPILE_VERSION VERSION_GREATER 6.9.9)
    add_compile_options(-Wimplicit-fallthrough)
  endif()
endif()

glob_subdirs()
