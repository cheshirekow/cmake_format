set(TANGENT_MODULES_DIR ${CMAKE_CURRENT_LIST_DIR}/tangent)

# =================================================
# Detect whether this is local or installed tooling
# =================================================
get_filename_component(_local_tooling_dir
                       ${CMAKE_CURRENT_LIST_DIR}/../../tangent/tooling ABSOLUTE)
if(EXISTS ${_local_tooling_dir})
  set(TANGENT_TOOLING ${_local_tooling_dir})
else()
  set(TANGENT_TOOLING ${TANGENT_MODULES_DIR})
endif()

# =================
# Submodules
# =================

# NOTE(josh): order matters
set(_tangent_modules
    environment.cmake
    wrappers.cmake
    codestyle.cmake
    ctest_helpers.cmake
    debian.cmake
    doctools.cmake
    pkgconfig.cmake
    re2-config.cmake)
foreach(module ${_tangent_modules})
  include(${TANGENT_MODULES_DIR}/${module})
endforeach()

if(TANGENT_SPARSE_EXPORT)
  message(STATUS "Detected sparse export: ${TANGENT_SPARSE_EXPORT}")
endif()

if(NOT TANGENT_BUILD_CONTEXT)
  set(TANGENT_BUILD_CONTEXT
      WORKSTATION
      CACHE STRING "what is the context for the current build")
endif()

# =================
# Global properties
# =================

# Will be populated by subdirectory listfiles with the dependencies of the
# master sphinx build
set_property(GLOBAL PROPERTY global_doc_files "")

# ======================
# Top-level (UI) targets
# ======================

add_custom_command(
  OUTPUT __always_rebuild
  COMMAND cmake -E echo "" > /dev/null
  COMMENT "Running every-build")

add_custom_target(chkfmt DEPENDS __always_rebuild)
add_custom_target(doc DEPENDS __always_rebuild)
add_custom_target(format DEPENDS __always_rebuild)
add_custom_target(gen DEPENDS __always_rebuild)
add_custom_target(lint DEPENDS __always_rebuild)
add_custom_target(precommit DEPENDS __always_rebuild)
add_custom_target(test-deps DEPENDS __always_rebuild)
add_custom_target(wheels DEPENDS __always_rebuild)

# ==================
# Codestyle Manifest
# ==================

if(CMAKE_GENERATOR STREQUAL "Ninja")
  add_custom_target(
    check-codestyle-manifest
    BYPRODUCTS ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake
    DEPENDS __always_rebuild
    COMMAND
      python -B ${TANGENT_TOOLING}/generate_style_manifest.py #
      --outfile ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake #
      --excludes-from ${CMAKE_SOURCE_DIR}/build_tooling/lint-excludes.txt #
      -- ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking for changes in codestyle manifest")
else()
  add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake
    DEPENDS __always_rebuild
    COMMAND
      python -B ${TANGENT_TOOLING}/generate_style_manifest.py #
      --outfile ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake #
      --excludes-from ${CMAKE_SOURCE_DIR}/build_tooling/lint-excludes.txt #
      -- ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking for changes in codestyle manifest")

  add_custom_target(check-codestyle-manifest
                    DEPENDS ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake)
endif()

check_call(
  COMMAND
    python -B ${TANGENT_TOOLING}/generate_style_manifest.py #
    --outfile ${CMAKE_BINARY_DIR}/codestyle_manifest.cmake #
    --excludes-from ${CMAKE_SOURCE_DIR}/build_tooling/lint-excludes.txt #
    -- ${CMAKE_SOURCE_DIR}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

check_call(
  COMMAND python -B ${TANGENT_TOOLING}/cmake_post.py --binary-dir
          ${CMAKE_BINARY_DIR} --generator "${CMAKE_GENERATOR}"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# If the manifest changes, then we need to rerun cmake to import link/fmt rules
# for the new manifest
# configure_file(${CMAKE_BINARY_DIR}/codestyle_manifest.cmake
# ${CMAKE_BINARY_DIR}/codestyle_manifest.stamp COPYONLY)

include(${CMAKE_BINARY_DIR}/codestyle_manifest.cmake)

# ========================
# Local python environment
# ========================

# Create python environment with packages needed to do the build
set(PYENV_WITNESS ${CMAKE_BINARY_DIR}/pyenv.witness)
set(PYENV
    ${CMAKE_COMMAND} -E env #
    VIRTUAL_ENV=${CMAKE_BINARY_DIR}/pyenv #
    "PATH=${CMAKE_BINARY_DIR}/pyenv:\$\${PATH}")

if(CMAKE_GENERATOR STREQUAL "Ninja")
  set(_depfile DEPFILE ${CMAKE_BINARY_DIR}/pyenv.d)
endif()

add_custom_command(
  OUTPUT ${PYENV_WITNESS}
  COMMAND rm -rf ${CMAKE_BINARY_DIR}/pyenv
  COMMAND virtualenv -p python3 ${CMAKE_BINARY_DIR}/pyenv
  COMMAND ${PYENV} pip install -r requirements.txt
  COMMAND echo "pyenv.witness : \\\\" > ${CMAKE_BINARY_DIR}/pyenv.d
  COMMAND
    env LC_ALL=C #
    find ${CMAKE_BINARY_DIR}/pyenv -type l,f #
    | sed 's: :\\\\ :g' #
    | sort #
    | sed 's:$$:\\\\:' >> ${CMAKE_BINARY_DIR}/pyenv.d
  COMMAND touch ${PYENV_WITNESS}
  DEPENDS requirements.txt
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Creating python environment" ${_depfile})

# NOTE(josh): bug in cmake 3.10. If we don't create this custom target, then
# cmake wont emit the rule... even though we have a rule later on that depends
# on the outputs of the custom command.
add_custom_target(pyenv DEPENDS ${PYENV_WITNESS})

# ==============
# doxygen target
# ==============

# NOTE(josh): some sparse checkouts don't include doxygen
if(EXISTS ${CMAKE_SOURCE_DIR}/doxy.config.in)
  # configure the doxygen configuration
  # NOTE(josh): maybe want to expose this for editor integration
  # ~~~
  # set(DOXY_WARN_FORMAT "\"$file($line) : $text \"")
  # set(DOXY_WARN_FORMAT "\"$file:$line: $text \"")
  # ~~~
  configure_file("${PROJECT_SOURCE_DIR}/doxy.config.in"
                 "${PROJECT_BINARY_DIR}/doxy.config")

  add_custom_command(
    OUTPUT ${PROJECT_BINARY_DIR}/doxy.stamp
    COMMAND doxygen ${PROJECT_BINARY_DIR}/doxy.config
    COMMAND touch ${PROJECT_BINARY_DIR}/doxy.stamp
    DEPENDS ${PROJECT_BINARY_DIR}/doxy.config
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(doxygen DEPENDS ${PROJECT_BINARY_DIR}/doxy.stamp)
  add_dependencies(doc doxygen)
endif()

# ==================
# better-test target
# ==================

add_custom_target(
  better-test
  DEPENDS test-deps
  COMMAND ctest --force-new-ctest-process --output-on-failure
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMENT "Execute ctest")

# ====================
# buildbot-test target
# ====================

add_custom_target(
  buildbot-test
  DEPENDS test-deps
  COMMAND
    # cmake-format: off
    ctest
    --label-exclude CI_DISABLED
    --force-new-ctest-process
    --output-on-failure
    --output-log ${CMAKE_BINARY_DIR}/ctestlog.txt
    # cmake-format: on
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

# =========
# git hooks
# =========

add_custom_target(pre-push)
add_dependencies(pre-push lint chkfmt)

add_custom_target(pre-release)
add_dependencies(pre-release better-test doc lint chkfmt)

# ========================
# bake vscode config files
# ========================

# Inform vscode where compile commands is
find_program(_python_path python)
file(GLOB _vscode_files ${CMAKE_SOURCE_DIR}/.vscode/*)
execute_process(
  COMMAND
    python -B ${TANGENT_TOOLING}/vscode_varsub.py #
    --var cmakeBinaryDir=${CMAKE_BINARY_DIR} #
    --var "pythonPath=${_python_path}" #
    sub ${_vscode_files}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(
  unsub-vscode
  COMMAND
    python -B ${TANGENT_TOOLING}/vscode_varsub.py #
    --var cmakeBinaryDir=${CMAKE_BINARY_DIR} #
    --var "pythonPath=${_python_path}" #
    --touch ${CMAKE_SOURCE_DIR}/CMakeLists.txt #
    unsub ${_vscode_files}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Restoring variables in vscode")
add_dependencies(precommit unsub-vscode)
