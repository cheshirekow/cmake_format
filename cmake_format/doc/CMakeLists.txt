#
# Generated source bits for sphinx documentation
#
set(_stage ${CMAKE_CURRENT_BINARY_DIR}/stage)
set(_genbits)

add_custom_command(
  OUTPUT ${_stage}/bits
  COMMAND ${CMAKE_COMMAND} -E make_directory ${_stage}/bits
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

set(_config_deps
    ../__main__.py #
    ../configuration.py #
    ../config_util.py)

add_custom_command(
  OUTPUT ${_stage}/bits/format-usage.txt
  COMMAND python -Bm cmake_format --help > ${_stage}/bits/format-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/format-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/format-usage-short.txt ${_stage}/bits/common-usage.txt
  COMMAND
    python -Bm cmake_format.tools.split_help ${_stage}/bits/format-usage.txt
    ${_stage}/bits/format-usage-short.txt ${_stage}/bits/common-usage.txt
  DEPENDS ${_stage}/bits/format-usage.txt ../tools/split_help.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/format-usage-short.txt
     ${_stage}/bits/common-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/annotate-usage.txt
  COMMAND python -Bm cmake_format.annotate --help >
          ${_stage}/bits/annotate-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} ../annotate.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/annotate-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/ctest-to-usage.txt
  COMMAND python -Bm cmake_format.ctest_to --help >
          ${_stage}/bits/ctest-to-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} ../ctest_to.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/ctest-to-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-usage.txt
  COMMAND python -Bm cmake_lint --help > ${_stage}/bits/lint-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} #
          ../../cmake_lint/__main__.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-usage-short.txt
  COMMAND python -Bm cmake_format.tools.split_help ${_stage}/bits/lint-usage.txt
          ${_stage}/bits/lint-usage-short.txt
  DEPENDS ${_stage}/bits/lint-usage.txt ../tools/split_help.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-usage-short.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/configbits.py
  COMMAND python -Bm cmake_format --dump-config > ${_stage}/bits/configbits.py
  DEPENDS ${_stage}/bits #
          ${_config_deps}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/configbits.py)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-in.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmake_lint/test/expect_lint.cmake
          ${_stage}/bits/lint-in.cmake
  DEPENDS ${_stage}/bits #
          ${CMAKE_SOURCE_DIR}/cmake_lint/test/expect_lint.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-in.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-out.cmake
  COMMAND python -Bm cmake_lint cmake_lint/test/expect_lint.cmake >
          ${_stage}/bits/lint-out.cmake || echo "OK"
  DEPENDS ${_stage}/bits #
          ../../cmake_lint/__main__.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-out.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-src.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmake_format/doc/bits/dump-example.cmake
          ${_stage}/bits/dump-example-src.cmake
  DEPENDS ${_stage}/bits #
          bits/dump-example.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-src.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-lex.txt
  COMMAND
    python -Bm cmake_format --dump lex ${_stage}/bits/dump-example-src.cmake >
    ${_stage}/bits/dump-example-lex.txt
  DEPENDS ${_stage}/bits #
          ../../cmake_format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-lex.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-parse.txt
  COMMAND
    python -Bm cmake_format --dump parse
    cmake_format/doc/bits/dump-example.cmake >
    ${_stage}/bits/dump-example-parse.txt
  DEPENDS ${_stage}/bits #
          ../../cmake_format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-parse.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-layout.txt
  COMMAND
    python -Bm cmake_format --dump layout
    cmake_format/doc/bits/dump-example.cmake >
    ${_stage}/bits/dump-example-layout.txt
  DEPENDS ${_stage}/bits #
          ../../cmake_format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-layout.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/example-in.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmake_format/test/test_in.cmake
          ${_stage}/bits/example-in.cmake
  DEPENDS ${_stage}/bits #
          ../test/test_in.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/example-in.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/example-out.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmake_format/test/test_out.cmake
          ${_stage}/bits/example-out.cmake
  DEPENDS ${_stage}/bits #
          ../test/test_out.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/example-out.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/lintimpl-table.rst
  COMMAND python -Bm cmake_lint.gendocs table >
          ${_stage}/bits/lintimpl-table.rst
  DEPENDS ${_stage}/bits #
          ../../cmake_lint/lintdb.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lintimpl-table.rst)

add_custom_command(
  OUTPUT ${_stage}/bits/features.rst
  COMMAND tail -n +5 cmake_format/doc/format-features.rst >
          ${_stage}/bits/features.rst
  DEPENDS ${_stage}/bits #
          format-features.rst
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/features.rst)

add_custom_command(
  OUTPUT ${_stage}/lint-implemented.rst
  COMMAND python -Bm cmake_lint.gendocs reference >
          ${_stage}/lint-implemented.rst
  DEPENDS ${_stage}/bits #
          ../../cmake_lint/lintdb.py ../../cmake_lint/gendocs.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/lint-implemented.rst)

add_custom_command(
  OUTPUT ${_stage}/example_rendered.html
  COMMAND python -Bm cmake_format.annotate --format iframe
          cmake_format/test/test_out.cmake > ${_stage}/example_rendered.html
  DEPENDS ${_stage}/bits #
          ../annotate.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/example_rendered.html)

add_custom_command(
  OUTPUT ${_stage}/configopts.rst
  COMMAND python -Bm cmake_format.tools.gen_config_details >
          ${_stage}/configopts.rst
  DEPENDS ../config_util.py #
          ../configuration.py #
          ../tools/gen_config_details.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/configopts.rst)

# TODO(josh): remove this iteration for just one file.
set(_genfiles)
set(_insource_genfiles README.rst)
foreach(_genfile ${_insource_genfiles})
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/${_genfile}
    COMMAND python -Bm cmake_format.doc.gendoc --bits ${_stage}/bits
            ${CMAKE_CURRENT_SOURCE_DIR}/${_genfile}
    # TODO(josh): not every file depends on every bit, so this is overkill, but
    # whatever... it's fine for now. We'll need more complicated code if we want
    # to actually declare which bits each file depends on.
    DEPENDS ${_genbits} gendoc.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/${_genfile})

  add_custom_target(
    run.cmake_format-doc-verify-${_genfile}
    COMMAND python -Bm cmake_format.doc.gendoc --verify --bits ${_stage}/bits
            ${CMAKE_CURRENT_SOURCE_DIR}/${_genfile}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_test(
    NAME cmake_format-doc-verify-${_genfile}
    COMMAND python -Bm cmake_format.doc.gendoc --verify --bits ${_stage}/bits
            ${CMAKE_CURRENT_SOURCE_DIR}/${_genfile}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()
add_custom_target(genbits-cmake_format DEPENDS ${_genbits})
add_dependencies(test-deps genbits-cmake_format)
add_custom_target(genfiles-cmake_format DEPENDS ${_genfiles})
add_dependencies(gen genfiles-cmake_format)

# copy sourcefiles from the sourcetree into the build tree so that they're all
# accessible from one tree
set(_copyfiles)
set(_docsources
    .readthedocs.yml
    bits/dump-example.cmake
    changelog.rst
    cmake-annotate.rst
    cmake-format.rst
    cmake-lint.rst
    configuration.rst
    conf.py
    contributing.rst
    ctest-to.rst
    custom_parsers.rst
    format-algorithm.rst
    format-case_studies.rst
    format-example.rst
    format-features.rst
    format-usage.rst
    index.rst
    installation.rst
    lint-example.rst
    lint-summary.rst
    lint-usage.rst
    modules.rst
    parse-algorithm.rst
    parse-automatic.rst
    parse-tree.rst
    release_notes.rst)
foreach(_docsource ${_docsources})
  add_custom_command(
    OUTPUT ${_stage}/${_docsource}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/${_docsource}
            ${_stage}/${_docsource}
    DEPENDS ${_docsource} ${_stage}/bits)
  list(APPEND _copyfiles ${_stage}/${_docsource})
endforeach()

# For the subproject build, also copy some of the common files into the build
# tree.
add_custom_command(
  OUTPUT ${_stage}/conf_common.py
  COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/doc/conf.py
          ${_stage}/conf_common.py)
list(APPEND _copyfiles ${_stage}/conf_common.py)

add_custom_command(
  OUTPUT ${_stage}/sphinx-static/css/cheshire_theme.css
  COMMAND
    ${CMAKE_COMMAND} -E copy
    ${CMAKE_SOURCE_DIR}/doc/sphinx-static/css/cheshire_theme.css
    ${_stage}/sphinx-static/css/cheshire_theme.css
  DEPENDS ${_stage}/bits)
list(APPEND _copyfiles ${_stage}/sphinx-static/css/cheshire_theme.css)

set(_tag pseudo-staging)
if(TRAVIS_TAG)
  set(_tag ${TRAVIS_TAG})
endif()
add_custom_command(
  OUTPUT ${_stage}/rtd-requirements.txt
  COMMAND python -Bm cmake_format.tools.gen_rtd_requirements ${_tag} ${_version}
          -o ${_stage}/rtd-requirements.txt
  DEPENDS ${CMAKE_SOURCE_DIR}/cmake_format/tools/gen_rtd_requirements.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/rtd-requirements.txt)

set(_sphinx_manifest ${_genbits} ${_copyfiles})
list(SORT _sphinx_manifest)

# NOTE(josh): cmake 3.10 does not have list(JOIN)
string(REPLACE ";" "\n" _manifest_text "${_sphinx_manifest}")

# NOTE(josh): don't use file(WRITE) because that wont create a dependency on the
# configure step to rerun cmake if the file is missing
configure_file(MANIFEST.in ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST
               NEWLINE_STYLE UNIX)

add_custom_target(
  clean-cmake_format-sphinx-stage
  DEPENDS ${_sphinx_manifest} ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST
  COMMAND python -Bm tangent.tooling.clean_stage
          ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST ${_stage}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Cleaning cmake_format/doc/stage")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M html ${_stage}
          ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS clean-cmake_format-sphinx-stage ${_sphinx_manifest}
          ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST ${CMAKE_SOURCE_DIR}/doc/conf.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Building sphinx documentation for cmake_format")

add_custom_target(doc-cmake_format
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/html/index.html)

add_custom_target(
  showdoc-cmake_format
  COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/html/index.html)

add_dependencies(doc doc-cmake_format)
set_property(GLOBAL APPEND PROPERTY global_doc_files ${_sphinx_manifest})

set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_MAKE_CLEAN_FILES
                                       ${_copyfiles} ${_genbits})

add_custom_target(
  push-cmake_format-github-pseudorelease-tag
  COMMAND python -Bm tangent.tooling.github create-pseudorelease-tag
          cheshirekow/cmake_format \$\${TRAVIS_BRANCH}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing psuedo-release tag")

set(_deploykey)
if(IS_TRAVIS_CI)
  set(_deploykey ${CMAKE_CURRENT_BINARY_DIR}/cmake-tools-rtd.deploy_key)
  add_custom_command(
    OUTPUT ${_deploykey}
    COMMAND
      # cmake-format: off
      openssl aes-256-cbc
      -K $ENV{encrypted_4bf912706780_key}
      -iv $ENV{encrypted_4bf912706780_iv}
      -in ${CMAKE_SOURCE_DIR}/tangent/tooling/deploy_keys/cmake-tools-rtd.enc
      -out ${_deploykey}
      -d
      # cmake-format: on
    COMMAND chmod 0600 ${_deploykey}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Decrypting cmake-tools-rtd.deploy_key")
endif()

add_custom_target(
  push-cmake_format-rtd-repo
  COMMAND
    # cmake-format: off
    python -Bm tangent.tooling.github sync-doc-artifacts
      --doc-repo git@github.com:cheshirekow/cmake-tools-rtd.git
      --repo-dir ${CMAKE_CURRENT_BINARY_DIR}/cmake-tools-rtd.git
      --scratch-tree ${CMAKE_CURRENT_BINARY_DIR}/scratch-tree
      --stage ${_stage}
      --deploy-key "${_deploykey}"
      --tag ${_tag}
    # cmake-format: on
  DEPENDS clean-cmake_format-sphinx-stage ${_sphinx_manifest} ${_deploykey}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing doc artifacts to the RTD repository")
