format_and_lint(cmake_format
                # cmake-format: sort
                __init__.py
                __main__.py
                annotate.py
                commands.py
                command_tests/add_custom_command_tests.py
                command_tests/add_executable_tests.py
                command_tests/add_library_tests.py
                command_tests/conditional_tests.py
                command_tests/export_tests.py
                command_tests/file_tests.py
                command_tests/__init__.py
                command_tests/install_tests.py
                command_tests/set_tests.py
                common.py
                configuration.py
                doc/conf.py
                doc/gendoc_sources.py
                formatter.py
                format_tests.py
                invocation_tests.py
                layout_tests.py
                lexer.py
                lexer_tests.py
                markup.py
                markup_tests.py
                parse_funs/add_executable.py
                parse_funs/add_library.py
                parse_funs/add_xxx.py
                parse_funs/external_project.py
                parse_funs/fetch_content.py
                parse_funs/file.py
                parse_funs/__init__.py
                parse_funs/install.py
                parser.py
                parser_tests.py
                pypi/setup.py
                render.py
                screw_users_test.py
                test/cmake-format.py
                tests.py)

add_test(NAME cmake_format-format_tests
         COMMAND python -m cmake_format.format_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-invocation_tests
         COMMAND python -m cmake_format.invocation_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-layout_tests
         COMMAND python -m cmake_format.layout_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-lexer_tests
         COMMAND python -m cmake_format.lexer_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-markup_tests
         COMMAND python -m cmake_format.markup_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-parser_tests
         COMMAND python -m cmake_format.parser_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

if(NOT IS_TRAVIS_CI)
  add_test(NAME cmake_format-format_tests_py3
           COMMAND python3 -m cmake_format.format_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-invocation_tests_py3
           COMMAND python3 -m cmake_format.invocation_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-layout_tests_py3
           COMMAND python3 -m cmake_format.layout_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-lexer_tests_py3
           COMMAND python3 -m cmake_format.lexer_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-markup_tests_py3
           COMMAND python3 -m cmake_format.markup_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  add_test(NAME cmake_format-parser_tests_py3
           COMMAND python3 -m cmake_format.parser_tests
           WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()

add_subdirectory(doc)
add_subdirectory(command_tests)
