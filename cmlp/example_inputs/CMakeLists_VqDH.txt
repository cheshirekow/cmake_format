#
# Test CMake version
#
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
#MARK_AS_ADVANCED( FORCE CMAKE_BACKWARDS_COMPATIBILITY )


###################################################
#                                                 #
#       Start project customization section       #
#                                                 #
###################################################

PROJECT(Orocos-KDL)

SET( KDL_VERSION 1.1.99 CACHE STRING "Version of Orocos KDL" )
STRING( REGEX MATCHALL "[0-9]+" KDL_VERSIONS ${KDL_VERSION} )
LIST( GET KDL_VERSIONS 0 KDL_VERSION_MAJOR)
LIST( GET KDL_VERSIONS 1 KDL_VERSION_MINOR)
LIST( GET KDL_VERSIONS 2 KDL_VERSION_PATCH)

SET(KDL_VERSION_PATCH "${KDL_VERSION_PATCH}")
MESSAGE( "Orocos KDL version ${VERSION} (${KDL_VERSION_MAJOR}.${KDL_VERSION_MINOR}.${KDL_VERSION_PATCH})" )

SET( PROJ_SOURCE_DIR ${Orocos-KDL_SOURCE_DIR} )
SET( PROJ_BINARY_DIR ${Orocos-KDL_BINARY_DIR} )


IF(NOT CMAKE_INSTALL_PREFIX)
  SET( CMAKE_INSTALL_PREFIX /usr/local/ CACHE PATH "Installation directory" FORCE)
  MESSAGE( STATUS "Setting installation directory to ${CMAKE_INSTALL_PREFIX}" )
ENDIF(NOT CMAKE_INSTALL_PREFIX)

SET(CMAKE_VERSION "${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}.${CMAKE_PATCH_VERSION}")


IF ( NOT CMAKE_BUILD_TYPE )
  SET(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build, options are: None(CMAKE_CXX_FLAGS or CMAKE_C_FLAGS used) Debug Release RelWithDebInfo MinSizeRel." FORCE)
  MESSAGE( "Setting build type to '${CMAKE_BUILD_TYPE}'" )
ELSE ( NOT CMAKE_BUILD_TYPE )
  MESSAGE( "Build type set to '${CMAKE_BUILD_TYPE}' by user." )
ENDIF ( NOT CMAKE_BUILD_TYPE )

SET( KDL_CFLAGS "" CACHE INTERNAL "")

find_package(Eigen 3.0 QUIET)
if(NOT Eigen_DIR)
include(${PROJ_SOURCE_DIR}/config/FindEigen3.cmake)
include_DIRECTORIES(${EIGEN3_INCLUDE_DIR})
endif()
INCLUDE_DIRECTORIES(${EIGEN_INCLUDE_DIRS})

INCLUDE (${PROJ_SOURCE_DIR}/config/DependentOption.cmake)

OPTION(ENABLE_TESTS OFF "Enable building of tests")
IF( ENABLE_TESTS )
  # If not in standard paths, set CMAKE_xxx_PATH's in environment, eg.
  # export CMAKE_INCLUDE_PATH=/opt/local/include
  # export CMAKE_LIBRARY_PATH=/opt/local/lib
  FIND_LIBRARY(CPPUNIT cppunit)
  SET(CPPUNIT ${CPPUNIT} "dl")
  FIND_PATH(CPPUNIT_HEADERS cppunit/TestRunner.h)
  IF ( CPPUNIT AND CPPUNIT_HEADERS)
    MESSAGE("-- Looking for Cppunit - found")
  ELSE ( CPPUNIT AND CPPUNIT_HEADERS )
    MESSAGE( FATAL_ERROR "-- Looking for Cppunit - not found")
  ENDIF ( CPPUNIT AND CPPUNIT_HEADERS )
ENDIF(ENABLE_TESTS )

OPTION(ENABLE_EXAMPLES OFF "Enable building of examples")

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)


add_definitions(-DEIGEN2_SUPPORT)

ADD_SUBDIRECTORY( doc )
ADD_SUBDIRECTORY( src )
ADD_SUBDIRECTORY( tests )
ADD_SUBDIRECTORY( examples )
ADD_SUBDIRECTORY( models )

CONFIGURE_FILE(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
  IMMEDIATE @ONLY)

CONFIGURE_FILE(${CMAKE_CURRENT_SOURCE_DIR}/KDLConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/orocos-kdl-config.cmake @ONLY)
INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/orocos-kdl-config.cmake DESTINATION share/orocos-kdl)

ADD_CUSTOM_TARGET(uninstall
  "${CMAKE_COMMAND}" -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")

############################################################
##                                                         #
## Setup PACKAGING                                         #
##                                                         #
############################################################

OPTION( CPACK_PACKAGES "Set to ON to build the packages. Requires cmake >2.4" OFF )
IF (CPACK_PACKAGES)

INCLUDE(InstallRequiredSystemLibraries)

# ATTENTION: There is sometimes a _SOURCE_ version of an
# option as well, set both if necessary !

# Create .tar.gz and .tar.tbz2 files:
SET(CPACK_GENERATOR "TBZ2")
SET(CPACK_SOURCE_GENERATOR "TBZ2")

# The plain 'package' target works correctly.
SET(CPACK_IGNORE_FILES        "/CVS/;/.svn/;.swp$;.#;/#;/build/")
# Since the 'package_source' target does a bold copy, define a list of
# files which should be excluded. Note that 'subpattern' matching is used,
# thus to exclude a directory use /mydir/
SET(CPACK_SOURCE_IGNORE_FILES "/CVS/;/.svn/;.swp$;.#;/#;/build/;~")

SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Orocos KDL")
SET(CPACK_PACKAGE_VENDOR "The Orocos Community")
SET(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README")
SET(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/COPYING")
SET(CPACK_PACKAGE_VERSION_MAJOR "${KDL_VERSION_MAJOR}")
SET(CPACK_PACKAGE_VERSION_MINOR "${KDL_VERSION_MINOR}")
SET(CPACK_PACKAGE_VERSION_PATCH "${KDL_VERSION_PATCH}")
SET(CPACK_PACKAGE_INSTALL_DIRECTORY "CMAKE ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}")
SET(CPACK_STRIP_FILES "bin/cmake")
#SET(CPACK_PACKAGE_EXECUTABLES "OrocosExec" "Orocos Executable")
INCLUDE(CPack)
ENDIF (CPACK_PACKAGES)
