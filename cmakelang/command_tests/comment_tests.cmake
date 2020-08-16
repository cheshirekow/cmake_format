# test: format_off_code
# No, I really want this to look ugly
# cmake-format: off
add_library(a b.cc
  c.cc         d.cc
          e.cc)
# cmake-format: on

# test: format_off_nested
add_custom_target(
  push-github-release
  COMMAND
    # cmake-format: off
    python -Bm cmakelang.tools.push_github_release
      --message ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
      $ENV{TRAVIS_TAG}
      ${_distdir}/cmake-format-${_version}.tar.gz
      ${_distdir}/cmake-format-${_version}-py3-none-any.whl
    # cmake-format: on
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_version}.md
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# test: multiline comment in statement
add_custom_target(
  my-target COMMAND foo bar baz # This comment is a trailing comment
                    # But this comment is a line comment
)

# test: comment attached at correct depth
ExternalProject_Add(
  FOO
  PREFIX ${FOO_PREFIX}
  TMP_DIR ${TMP_DIR}
  STAMP_DIR ${FOO_PREFIX}/stamp
  # Download
  DOWNLOAD_DIR ${DOWNLOAD_DIR}
  DOWNLOAD_NAME ${FOO_ARCHIVE_FILE_NAME}
  URL ${STORAGE_URL}/${FOO_ARCHIVE_FILE_NAME}
  URL_MD5 ${FOO_MD5}
  # Patch
  PATCH_COMMAND ${PATCH_COMMAND} ${PROJECT_SOURCE_DIR}/patch.diff
  # Configure
  SOURCE_DIR ${SRC_DIR}
  CMAKE_ARGS ${CMAKE_OPTS}
  # Build
  BUILD_IN_SOURCE 1
  BUILD_BYPRODUCTS ${CUR_COMPONENT_ARTIFACTS}
  # Logging
  LOG_CONFIGURE 1
  LOG_BUILD 1
  LOG_INSTALL 1)

# test: comment_depth_doesnt_overbreak
#[==[
if(FOO_FOUND)
  ExternalProject_Add(
    FOO
    PREFIX ${FOO_PREFIX}
    TMP_DIR ${TMP_DIR}
# This comment belongs to the statement group
  )
endif()
]==]
if(FOO_FOUND)
  ExternalProject_Add(
    FOO
    PREFIX ${FOO_PREFIX}
    TMP_DIR ${TMP_DIR}
    # This comment belongs to the statement group
  )
endif()
