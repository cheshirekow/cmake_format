set(additional_sources example_rendered.html)

add_custom_target(
  scanrst-cmake_format_docs
  COMMAND python -B ${CMAKE_SOURCE_DIR}/doc/find_rst.py
          --manifest-path ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
          --touch ${CMAKE_SOURCE_DIR}/cmake_format
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

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
  COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M
          html ${CMAKE_CURRENT_SOURCE_DIR}
          ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND touch
          ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
  DEPENDS conf.py
          ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
          ${CMAKE_SOURCE_DIR}/doc/conf.py
          ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
          ${additional_sources}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(
  cmake_format-doc
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)

add_custom_target(
  show-cmake_format-doc
  COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
)

add_dependencies(doc cmake_format-doc)

add_custom_target(
  gendoc_sources-cmake_format
  COMMAND python -B gendoc_sources.py
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "Replacing dynamic text in documentation sources for cmake_format")

add_test(NAME cmake_format-docsources-test
         COMMAND python -B gendoc_sources.py --verify
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
