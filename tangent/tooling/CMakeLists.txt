add_custom_target(
  update-export
  COMMAND python -B ${TANGENT_TOOLING}/export_sparse_subrepo.py update
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Updating sparse export")

add_custom_target(
  verify-export
  COMMAND python -B ${TANGENT_TOOLING}/export_sparse_subrepo.py verify
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "verify sparse export")

add_test(
  NAME verify-export
  COMMAND python -B ${TANGENT_TOOLING}/export_sparse_subrepo.py verify
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_build_scripts
    broadway_run.py
    check_pbuilderrc.py
    clean_stage.py
    cmake_post.py
    debhelp.py
    export_sparse_subrepo.py
    generate_style_manifest.py
    get_release_notes.py
    get_version_from_header.py
    github.py
    gtkdoc_helper.py
    install_debug_symbols.py
    sync_sparse.py
    vscode_varsub.py)

set(_cmake_modules
    codestyle.cmake
    ctest_helpers.cmake
    debian.cmake
    doctools.cmake
    environment.cmake
    pkgconfig.cmake
    re2-config.cmake
    wrappers.cmake)
unset(_cmake_modules_fullpaths)
foreach(module ${_cmake_modules})
  list(APPEND _cmake_modules_fullpaths ${TANGENT_MODULES_DIR}/${module})
endforeach()

install(FILES ${CMAKE_SOURCE_DIR}/build_tooling/cmake/tangent.cmake
        DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/cmake/Modules")

install(FILES ${_build_scripts} ${_cmake_modules_fullpaths}
        DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/cmake/Modules/tangent")
