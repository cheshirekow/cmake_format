add_custom_target(
  scanrst-cmake_format_docs
  COMMAND
    python -B ${CMAKE_SOURCE_DIR}/doc/find_rst.py --manifest-path
    ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt --touch
    ${CMAKE_SOURCE_DIR}/cmake_format
  DEPENDS ${CMAKE_SOURCE_DIR}/doc/find_rst.py
  BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Scanning RST for cmake_format")

if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
    DEPENDS scanrst-cmake_format_docs
    COMMENT "Stubbing RST scan for cmake_format_doc")
endif()

set(gendoc_sources_
    ${CMAKE_CURRENT_SOURCE_DIR}/README.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/configuration.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake-annotate.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake-format.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake-lint.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/ctest-to.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/example.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/example_rendered.html
    ${CMAKE_CURRENT_SOURCE_DIR}/lint-example.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/lint-implemented.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/lint-usage.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/parse_tree.rst
    ${CMAKE_CURRENT_SOURCE_DIR}/usage.rst)

add_custom_target(
  gendoc_sources-cmake_format
  COMMAND python -Bm cmake_format.doc.gendoc_sources
  DEPENDS gendoc_sources.py ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
  BYPRODUCTS ${gendoc_sources_}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Generating files for cmake-format")

if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
  add_custom_command(
    OUTPUT ${gendoc_sources_}
    DEPENDS gendoc_sources-cmake_format
    COMMENT "Stubbing gendocs for cmake_format_doc")
endif()

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
  COMMAND
    env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M html
    ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
  DEPENDS conf.py
          ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
          ${CMAKE_SOURCE_DIR}/doc/conf.py
          ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
          ${gendoc_sources_}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(cmake_format-doc
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)

add_custom_target(
  show-cmake_format-doc
  COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)

add_dependencies(doc cmake_format-doc)

add_test(
  NAME cmake_format-docsources-test
  COMMAND python -Bm cmake_format.doc.gendoc_sources --verify
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
