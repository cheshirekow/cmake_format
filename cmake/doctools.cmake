# porcelain for documentation generation tools

# Run sphinx
#
# usage:
# ~~~
# sphinx(<module>
#        changlog.rst
#        index.rst
#        todo.rst
#        README.rst)
# ~~~

function(sphinx module)
  set(stamp_path_ ${CMAKE_CURRENT_BINARY_DIR}/${module}_doc.stamp)
  add_custom_command(
    OUTPUT ${stamp_path_}
    COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR}
            sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND touch ${stamp_path_}
    DEPENDS ${ARGN}
            conf.py
            ${CMAKE_SOURCE_DIR}/doc/conf.py
            ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_custom_target(${module}-doc DEPENDS ${stamp_path_})
  add_custom_target(
    show-${module}-doc
    COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp
  )
  add_dependencies(doc ${module}-doc)
endfunction()
