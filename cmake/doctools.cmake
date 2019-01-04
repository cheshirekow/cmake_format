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
  add_custom_command(OUTPUT ${stamp_path_}
                     COMMAND sphinx-build -M html ${CMAKE_CURRENT_SOURCE_DIR}
                             ${CMAKE_CURRENT_BINARY_DIR}
                     COMMAND touch ${stamp_path_}
                     DEPENDS ${ARGN}
                     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_custom_target(${module}_doc DEPENDS ${stamp_path_})
  add_dependencies(doc ${module}_doc)
endfunction()

