set(_testnames format.invocation_tests format.layout_tests lex.tests
               markup_tests parse.tests)

foreach(testname ${_testnames})
  tangent_addtest(
    NAME cmakelang-${testname}
    COMMAND python -Bm cmakelang.${testname}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

if(NOT IS_TRAVIS_CI)
  foreach(testname ${_testnames})
    tangent_addtest(
      NAME cmakelang-${testname}_py3
      COMMAND python3 -Bm cmakelang.${testname}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  endforeach()
endif()

set(_genfiles)
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/parse/variables.py
  COMMAND python -Bm cmakelang.tools.parse_cmake_help --outfile
          cmakelang/parse/variables.py variables
  DEPENDS tools/parse_cmake_help.py tools/variables.jinja.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Generating variables.py")
list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/parse/variables.py)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/parse/properties.py
  COMMAND python -Bm cmakelang.tools.parse_cmake_help --outfile
          cmakelang/parse/properties.py properties
  DEPENDS tools/parse_cmake_help.py tools/properties.jinja.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Generating properties.py")
list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/parse/properties.py)

add_custom_target(gen-cmakelang DEPENDS ${_genfiles})
add_dependencies(gen gen-cmakelang)

# NOTE(josh): this is just here to induce a dependency on the configure step. If
# we change the version number in __init__.py we need to re-run cmake so we can
# get out the version number and create rules for the distribution files.
configure_file(__init__.py init.stamp COPYONLY)

check_pyoneline(
  "from __future__ import print_function" #
  "import cmakelang" #
  "print(cmakelang.__version__)" #
  OUTPUT_VARIABLE _src_version)

check_pyoneline(
  "from __future__ import print_function" #
  "import cmakelang" #
  "from packaging import version" #
  "print(version.parse(cmakelang.__version__).is_devrelease)"
  OUTPUT_VARIABLE _is_devrelease)

# NOTE(josh): python uses dot to separate pre-release while node uses dash
string(REGEX REPLACE "([0-9]+\\.[0-9]+\\.[0-9]+)\\.(.*)" "\\1-\\2"
                     _extension_version "${_src_version}")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/.egg
  COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/.egg
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_python_packages cmakelang cmake_annotate cmake_format cmake_lint
                     cmake_parse)

set(_distdir ${CMAKE_CURRENT_BINARY_DIR}/dist)
foreach(package ${_python_packages})
  string(REPLACE "_" "-" dashpackage "${package}")
  set(_pypi_artifacts_${package}
      ${_distdir}/${dashpackage}-${_src_version}.tar.gz
      ${_distdir}/${package}-${_src_version}-py3-none-any.whl)
  list(APPEND _pypi_artifacts ${_pypi_artifacts_${package}})
endforeach()

add_custom_command(
  OUTPUT ${_pypi_artifacts}
  COMMAND
    # cmake-format: off
    python cmakelang/pypi/setup.py
    build --build-base ${CMAKE_CURRENT_BINARY_DIR}
    egg_info --egg-base ${CMAKE_CURRENT_BINARY_DIR}/.egg
    bdist_wheel
      --bdist-dir ${CMAKE_CURRENT_BINARY_DIR}/bdist
      --dist-dir ${_distdir}
    sdist --dist-dir ${_distdir}
    # cmake-format: on
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/.egg
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(
  cmakelang-wheel
  DEPENDS ${_distdir}/cmakelang-${_src_version}-py3-none-any.whl)
add_dependencies(wheels cmakelang-wheel)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  DEPENDS doc/release_notes.rst ${TANGENT_TOOLING}/get_release_notes.py
  COMMAND
    # cmake-format: off
    python -B ${TANGENT_TOOLING}/get_release_notes.py
      ${CMAKE_CURRENT_SOURCE_DIR}/doc/release_notes.rst ${_src_version}
      -o ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
    # cmake-format: on
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_releasenote_path
    ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.md)
add_custom_command(
  OUTPUT ${_releasenote_path}
  COMMAND pandoc -s -o ${_releasenote_path}
          ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/release_notes-${_src_version}.rst
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_keydir ${CMAKE_SOURCE_DIR}/tangent/tooling/deploy_keys)
set(_docker_keyid "eadc5618fa58")
set(_precommit_keyid "616260d3147f")

foreach(slug docker precommit)
  unset(_${slug}_deploykey)
  set(_outfile ${CMAKE_CURRENT_BINARY_DIR}/cmakelang-${slug}.deploy_key)
  get_filename_component(_${slug}_deploykey ${_outfile} ABSOLUTE)
  travis_decrypt(${_outfile} ${_keydir}/cmakelang-${slug}.enc ${_${slug}_keyid})
endforeach()

glob_subdirs()

add_custom_target(
  push-cmakelang-github-pseudorelease-tag
  COMMAND python -B ${TANGENT_TOOLING}/github.py create-pseudorelease-tag
          cheshirekow/cmake_format \$\${TRAVIS_BRANCH}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing psuedo-release tag")

set(_vscedir ${CMAKE_CURRENT_BINARY_DIR}/vscode_extension)
add_custom_target(
  push-cmakelang-github-release
  DEPENDS ${_releasenote_path} ${_pypi_artifacts}
          # ${_vscedir}/cmake-format-${_extension_version}.vsix
  COMMAND
    # cmake-format: off
    python -B ${TANGENT_TOOLING}/github.py push-release
      --message ${_releasenote_path}
      --repo-slug cheshirekow/cmake_format
      --tag "v${_src_version}"
      ${_distdir}/cmakelang-${_src_version}.tar.gz
      ${_distdir}/cmakelang-${_src_version}-py3-none-any.whl
      ${_vscedir}/cmake-format-${_extension_version}.vsix
    # cmake-format: on
  COMMENT "Uploading release artifacts"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# NOTE(josh): cmake is broken. It fails to produce an accurate build system when
# we correctly specify the .vsix path in the above rule. We must use target
# level dependencies to get the correct order of operations and then omit the
# actual file-level dependency.
add_dependencies(push-cmakelang-github-release vscode-extension)

travis_decrypt(${CMAKE_CURRENT_BINARY_DIR}/pypi-tokens.json
               ${_keydir}/cmakelang-pypi-tokens.json.enc "db380b4cb002")

foreach(package ${_python_packages})
  unset(_twineargs)
  if(_is_devrelease)
    list(APPEND _twineargs --repository testpypi)
  endif()

  unset(_twinedeps)
  if(IS_TRAVIS_CI)
    set(_pypirc ${CMAKE_CURRENT_BINARY_DIR}/pypirc-${package})
    list(APPEND _twineargs --config-file ${_pypirc})
    list(APPEND _twinedeps ${_pypirc})

    add_custom_command(
      OUTPUT ${_pypirc}
      DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/pypi-tokens.json
              ../tangent/tooling/write_pypirc.py
      COMMAND
        python -Bm tangent.tooling.write_pypirc #
        --outfile ${_pypirc} #
        --tokens-from ${CMAKE_CURRENT_BINARY_DIR}/pypi-tokens.json #
        --package ${package}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
      COMMENT "Writing ${_pypirc}")
  endif()

  add_custom_target(
    push-cmakelang-pypi-${package}
    DEPENDS ${_pypi_artifacts_${package}} ${_twinedeps}
    COMMAND twine upload --skip-existing ${_twineargs}
            ${_pypi_artifacts_${package}}
    COMMENT "Uploading ${package} to pypi"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()

add_custom_target(push-cmakelang-pypi-release)
add_dependencies(push-cmakelang-pypi-release push-cmakelang-pypi-cmakelang
                 push-cmakelang-pypi-cmake_format)

add_custom_target(
  push-cmakelang-precommit
  DEPENDS ${_precommit_deploykey}
  COMMAND
    python -B ${CMAKE_CURRENT_SOURCE_DIR}/tools/ensure_precommit_tag.py
    --version ${_src_version} --deploykey ${_precommit_deploykey} --workdir
    ${CMAKE_CURRENT_BINARY_DIR}/precommit-scratch
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing precommit release tag")

add_custom_target(
  push-cmakelang-docker
  DEPENDS ${_docker_deploykey}
  COMMAND
    python -B ${CMAKE_CURRENT_SOURCE_DIR}/tools/ensure_docker_tag.py --version
    ${_src_version} --deploykey ${_docker_deploykey} --workdir
    ${CMAKE_CURRENT_BINARY_DIR}/docker-scratch
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing docker release tag")

set(_release_targets
    push-cmakelang-github-release push-cmakelang-rtd-repo
    push-cmakelang-pypi-release push-cmakelang-precommit push-cmakelang-docker)

add_custom_target(release-cmakelang)
add_dependencies(release-cmakelang ${_release_targets})

# foreach(target ${_release_targets}) add_dependencies(${target} best-test)
# endforeach()
