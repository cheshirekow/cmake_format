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
    COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M html
            ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND touch ${stamp_path_}
    DEPENDS ${ARGN} conf.py ${CMAKE_SOURCE_DIR}/doc/conf.py
            ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_custom_target(${module}-doc DEPENDS ${stamp_path_})
  add_custom_target(
    show-${module}-doc
    COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_doc.stamp)
  add_dependencies(doc ${module}-doc)
endfunction()

# Run sphinx
#
# usage:
# ~~~
# autosphinx(
#   module
#   ADDITIONAL_SOURCES [source1, [source2, [...]]]
# )
# ~~~
function(autosphinx module)
  set(_options)
  set(_one_value_args)
  set(_multi_value_args ADDITIONAL_SOURCES)
  cmake_parse_arguments(arg "${_options}" "${_one_value_args}"
                        "${_multi_value_args}" ${ARGN})

  add_custom_target(
    scanrst-${module}-doc
    COMMAND
      python -B ${CMAKE_SOURCE_DIR}/doc/find_rst.py --manifest-path
      ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt --touch
      ${CMAKE_SOURCE_DIR}/${module}
    DEPENDS ${CMAKE_SOURCE_DIR}/doc/find_rst.py
    BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Scanning RST for ${module}")

  if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
      DEPENDS scanrst-${module}_docs
      COMMENT "Stubbing RST scan for ${module}_doc")
  endif()

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${module}_doc.stamp
    COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M html
            ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/${module}_doc.stamp
    DEPENDS conf.py
            ${CMAKE_CURRENT_BINARY_DIR}/rst_manifest.txt
            ${CMAKE_SOURCE_DIR}/doc/conf.py
            ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
            ${args_ADDITIONAL_SOURCES}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(${module}-doc
                    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${module}_doc.stamp)

  add_custom_target(
    show-${module}-doc
    COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${module}_doc.stamp)

  add_dependencies(doc ${module}-doc)

endfunction()

# Generate rules to copy a list of files into a common directory at build time
function(stage_files)
  cmake_parse_arguments(_args "" "SOURCEDIR;STAGE;LIST" "FILES" ${ARGN})
  set(_copyfiles ${${_args_LIST}})
  foreach(_copyfile ${_args_FILES})
    if("${_copyfile}" MATCHES "([^:]+):([^:]+)")
      set(_srcfile ${CMAKE_MATCH_1})
      set(_tgtfile ${CMAKE_MATCH_2})
    else()
      set(_srcfile "${_copyfile}")
      set(_tgtfile "${_copyfile}")
    endif()
    add_custom_command(
      OUTPUT ${_args_STAGE}/${_tgtfile}
      COMMAND ${CMAKE_COMMAND} -E copy ${_args_SOURCEDIR}/${_srcfile}
              ${_args_STAGE}/${_tgtfile}
      DEPENDS ${_args_SOURCEDIR}/${_srcfile})
    list(APPEND _copyfiles ${_args_STAGE}/${_tgtfile})
  endforeach()
  set(${_args_LIST}
      ${_copyfiles}
      PARENT_SCOPE)
endfunction()
