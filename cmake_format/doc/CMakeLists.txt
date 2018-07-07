set(cmake_format_docs
    conf.py
    changelog.rst
    index.rst
    format_algorithm.rst
    parse_tree.rst
    todo.rst
    README.rst)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
                   COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
                           ${CMAKE_CURRENT_BINARY_DIR}
                   COMMAND touch
                           ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
                   DEPENDS ${cmake_format_docs}
                   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_custom_target(cmake_format_doc
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)
add_dependencies(doc cmake_format_doc)
