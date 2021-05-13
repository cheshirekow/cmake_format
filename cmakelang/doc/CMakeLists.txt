#
# Generated source bits for sphinx documentation
#
set(_stage ${CMAKE_CURRENT_BINARY_DIR}/stage)
set(_genbits)

add_custom_command(
  OUTPUT ${_stage}/bits
  COMMAND ${CMAKE_COMMAND} -E make_directory ${_stage}/bits
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Creating directory ${_stage}/bits")

set(_config_deps ../configuration.py #
                 ../config_util.py)

add_custom_command(
  OUTPUT ${_stage}/bits/format-usage.txt
  COMMAND python -Bm cmakelang.format --help > ${_stage}/bits/format-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/format-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/format-usage-short.txt ${_stage}/bits/common-usage.txt
  COMMAND python -Bm cmakelang.tools.split_help ${_stage}/bits/format-usage.txt
          ${_stage}/bits/format-usage-short.txt ${_stage}/bits/common-usage.txt
  DEPENDS ${_stage}/bits/format-usage.txt ../tools/split_help.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/format-usage-short.txt
     ${_stage}/bits/common-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/annotate-usage.txt
  COMMAND python -Bm cmakelang.annotate --help >
          ${_stage}/bits/annotate-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} ../annotate.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/annotate-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/ctest-to-usage.txt
  COMMAND python -Bm cmakelang.ctest_to --help >
          ${_stage}/bits/ctest-to-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} ../ctest_to.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/ctest-to-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-usage.txt
  COMMAND python -Bm cmakelang.lint --help > ${_stage}/bits/lint-usage.txt
  DEPENDS ${_stage}/bits #
          ${_config_deps} #
          ../lint/__main__.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-usage.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-usage-short.txt
  COMMAND python -Bm cmakelang.tools.split_help ${_stage}/bits/lint-usage.txt
          ${_stage}/bits/lint-usage-short.txt
  DEPENDS ${_stage}/bits/lint-usage.txt ../tools/split_help.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-usage-short.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/configbits.py
  COMMAND python -Bm cmakelang.format --dump-config >
          ${_stage}/bits/configbits.py
  DEPENDS ${_stage}/bits #
          ${_config_deps}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/configbits.py)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-in.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmakelang/lint/test/expect_lint.cmake
          ${_stage}/bits/lint-in.cmake
  DEPENDS ${_stage}/bits #
          ${CMAKE_SOURCE_DIR}/cmakelang/lint/test/expect_lint.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-in.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/lint-out.cmake
  COMMAND python -Bm cmakelang.lint cmakelang/lint/test/expect_lint.cmake >
          ${_stage}/bits/lint-out.cmake || echo "OK"
  DEPENDS ${_stage}/bits #
          ../lint/__main__.py #
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lint-out.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-src.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmakelang/doc/bits/dump-example.cmake
          ${_stage}/bits/dump-example-src.cmake
  DEPENDS ${_stage}/bits #
          bits/dump-example.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-src.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-lex.txt
  COMMAND
    python -Bm cmakelang.format --dump lex ${_stage}/bits/dump-example-src.cmake
    > ${_stage}/bits/dump-example-lex.txt
  DEPENDS ${_stage}/bits #
          ../format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-lex.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-parse.txt
  COMMAND
    python -Bm cmakelang.format --dump parse
    cmakelang/doc/bits/dump-example.cmake >
    ${_stage}/bits/dump-example-parse.txt
  DEPENDS ${_stage}/bits #
          ../format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-parse.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/dump-example-layout.txt
  COMMAND
    python -Bm cmakelang.format --dump layout
    cmakelang/doc/bits/dump-example.cmake >
    ${_stage}/bits/dump-example-layout.txt
  DEPENDS ${_stage}/bits #
          ../format/__main__.py #
          ${_stage}/bits/dump-example-src.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/dump-example-layout.txt)

add_custom_command(
  OUTPUT ${_stage}/bits/example-in.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmakelang/format/testdata/test_in.cmake
          ${_stage}/bits/example-in.cmake
  DEPENDS ${_stage}/bits #
          ../format/testdata/test_in.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/example-in.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/example-out.cmake
  COMMAND ${CMAKE_COMMAND} -E copy cmakelang/format/testdata/test_out.cmake
          ${_stage}/bits/example-out.cmake
  DEPENDS ${_stage}/bits #
          ../format/testdata/test_out.cmake
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/example-out.cmake)

add_custom_command(
  OUTPUT ${_stage}/bits/lintimpl-table.rst
  COMMAND python -Bm cmakelang.lint.gendocs table >
          ${_stage}/bits/lintimpl-table.rst
  DEPENDS ${_stage}/bits #
          ../lint/lintdb.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/lintimpl-table.rst)

add_custom_command(
  OUTPUT ${_stage}/bits/features.rst
  COMMAND tail -n +5 cmakelang/doc/format-features.rst >
          ${_stage}/bits/features.rst
  DEPENDS ${_stage}/bits #
          format-features.rst
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/bits/features.rst)

add_custom_command(
  OUTPUT ${_stage}/lint-implemented.rst
  COMMAND python -Bm cmakelang.lint.gendocs reference >
          ${_stage}/lint-implemented.rst
  DEPENDS ${_stage}/bits #
          ../lint/lintdb.py ../lint/gendocs.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/lint-implemented.rst)

add_custom_command(
  OUTPUT ${_stage}/example_rendered.html
  COMMAND
    python -Bm cmakelang.annotate --format iframe
    cmakelang/format/testdata/test_out.cmake > ${_stage}/example_rendered.html
  DEPENDS ${_stage}/bits #
          ../annotate.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/example_rendered.html)

add_custom_command(
  OUTPUT ${_stage}/configopts.rst
  COMMAND python -Bm cmakelang.tools.gen_config_details >
          ${_stage}/configopts.rst
  DEPENDS ../config_util.py #
          ../configuration.py #
          ../tools/gen_config_details.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
list(APPEND _genbits ${_stage}/configopts.rst)

# TODO(josh): remove this iteration for just one file.
set(_genfiles)
set(_insource_genfiles README.rst)
foreach(genfile ${_insource_genfiles})
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/${genfile}
    COMMAND python -B ${TANGENT_TOOLING}/gendoc.py --bits ${_stage}/bits
            ${CMAKE_CURRENT_SOURCE_DIR}/${genfile}
    # TODO(josh): not every file depends on every bit, so this is overkill, but
    # whatever... it's fine for now. We'll need more complicated code if we want
    # to actually declare which bits each file depends on.
    DEPENDS ${_genbits} ${TANGENT_TOOLING}/gendoc.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  list(APPEND _genfiles ${CMAKE_CURRENT_SOURCE_DIR}/${genfile})

  tangent_addtest(
    NAME cmakelang-doc-verify-${genfile}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${genfile}
    COMMAND python -B ${TANGENT_TOOLING}/gendoc.py --verify --bits
            ${_stage}/bits ${CMAKE_CURRENT_SOURCE_DIR}/${genfile}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endforeach()
add_custom_target(genbits-cmakelang DEPENDS ${_genbits})
add_dependencies(test-deps genbits-cmakelang)
add_custom_target(genfiles-cmakelang DEPENDS ${_genfiles})
add_dependencies(gen genfiles-cmakelang)

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
    lint-inline.rst
    lint-notes.rst
    lint-summary.rst
    lint-usage.rst
    modules.rst
    parse-algorithm.rst
    parse-automatic.rst
    parse-tree.rst
    release_notes.rst
    release_process.rst
    release-pipeline.svg)
foreach(docsource ${_docsources})
  add_custom_command(
    OUTPUT ${_stage}/${docsource}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/${docsource}
            ${_stage}/${docsource}
    DEPENDS ${docsource} ${_stage}/bits)
  list(APPEND _copyfiles ${_stage}/${docsource})
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

add_custom_command(
  OUTPUT ${_stage}/rtd-requirements.txt
  COMMAND
    python -B ${TANGENT_TOOLING}/gen_rtd_requirements.py --tag from-travis
    --version ${_src_version} -o ${_stage}/rtd-requirements.txt
    ${CMAKE_CURRENT_SOURCE_DIR}/rtd-requirements.txt.in
  DEPENDS ${TANGENT_TOOLING}/gen_rtd_requirements.py
          ${CMAKE_CURRENT_SOURCE_DIR}/rtd-requirements.txt.in
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
  clean-cmakelang-sphinx-stage
  DEPENDS ${_sphinx_manifest} ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST
  COMMAND python -B ${TANGENT_TOOLING}/clean_stage.py
          ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST ${_stage}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Cleaning cmakelang/doc/stage")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  COMMAND env PYTHONPATH=${CMAKE_SOURCE_DIR} sphinx-build -M html ${_stage}
          ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS clean-cmakelang-sphinx-stage ${_sphinx_manifest}
          ${CMAKE_CURRENT_BINARY_DIR}/MANIFEST ${CMAKE_SOURCE_DIR}/doc/conf.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Building sphinx documentation for cmakelang")

add_custom_target(doc-cmakelang
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/html/index.html)

add_custom_target(
  showdoc-cmakelang
  COMMAND xdg-open ${CMAKE_CURRENT_BINARY_DIR}/html/index.html
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/html/index.html)

add_dependencies(doc doc-cmakelang)
set_property(GLOBAL APPEND PROPERTY global_doc_files ${_sphinx_manifest})

set_property(
  DIRECTORY
  APPEND
  PROPERTY ADDITIONAL_MAKE_CLEAN_FILES ${_copyfiles} ${_genbits})

set(_deploykey ${CMAKE_CURRENT_BINARY_DIR}/cmakelang-rtd.deploy_key)
set(_deploykey_src
    ${CMAKE_SOURCE_DIR}/tangent/tooling/deploy_keys/cmakelang-rtd.enc)
travis_decrypt(${_deploykey} ${_deploykey_src} "4bf912706780")

add_custom_target(
  push-cmakelang-rtd-repo
  COMMAND
    # cmake-format: off
    python -B ${TANGENT_TOOLING}/github.py sync-doc-artifacts
      --doc-repo git@github.com:cheshirekow/cmake-tools-rtd.git
      --repo-dir ${CMAKE_CURRENT_BINARY_DIR}/cmake-tools-rtd.git
      --scratch-tree ${CMAKE_CURRENT_BINARY_DIR}/scratch-tree
      --stage ${_stage}
      --deploy-key "${_deploykey}"
      --tag "v${_src_version}"
    # cmake-format: on
  DEPENDS clean-cmakelang-sphinx-stage ${_sphinx_manifest} ${_deploykey}
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Pushing doc artifacts to the RTD repository")
