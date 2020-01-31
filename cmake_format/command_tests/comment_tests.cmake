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
    python -Bm cmake_format.tools.push_github_release
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
