set(additional_sources example_rendered.html)

add_custom_target(
  scanrst-cmake_format_docs
  COMMAND python -B ${CMAKE_SOURCE_DIR}/doc/find_rst.py
          --manifest-path ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
          --touch ${CMAKE_SOURCE_DIR}/cmake_format
  DEPENDS ${CMAKE_SOURCE_DIR}/doc/find_rst.py BYPRODUCTS
          ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Scanning RST for cmake_format")

# NOTE(josh): might be needed for non-ninja builds (makefile?)
# add_custom_command( OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
# DEPENDS scanrst-cmake_format_doc COMMENT "Stubbing RST scan for
# cmake_format_doc")

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
                   COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M
                           html ${CMAKE_CURRENT_SOURCE_DIR}
                           ${CMAKE_CURRENT_BINARY_DIR}
                   COMMAND touch
                           ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
                   DEPENDS ${CMAKE_SOURCE_DIR}/doc/conf.py
                           ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
                           ${additional_sources}
                   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(cmake_format_doc
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)

add_dependencies(doc cmake_format_doc)
