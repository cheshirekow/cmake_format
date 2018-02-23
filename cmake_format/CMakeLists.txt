set(cmake_format_py_files
    __init__.py
    __main__.py
    commands.py
    configuration.py
    formatter.py
    lexer.py
    markup.py
    parser.py
    lexer_tests.py
    markup_tests.py
    parser_tests.py
    format_tests.py
    tests.py)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_format.stamp
                   COMMAND autopep8 -i ${cmake_format_py_files}
                   COMMAND python -Bm cmake_format -i CMakeLists.txt
                           doc/CMakeLists.txt test/CMakeLists.txt
                   COMMAND touch
                           ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_format.stamp
                   DEPENDS ${cmake_format_py_files}
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_custom_target(cmake_format_format
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_format.stamp)
add_dependencies(format cmake_format_format)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_lint.stamp
                   COMMAND pylint ${cmake_format_py_files}
                   COMMAND touch
                           ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_lint.stamp
                   DEPENDS ${cmake_format_py_files}
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_custom_target(cmake_format_lint
                  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake_format_lint.stamp)

# NOTE(josh): format before lint-check, avoid formatting lint
add_dependencies(cmake_format_lint cmake_format_format)
add_dependencies(lint cmake_format_lint)

add_test(NAME cmake_format-format_tests
         COMMAND python -m cmake_format.format_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-invocation_tests
         COMMAND python -m cmake_format.invocation_tests
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

add_test(NAME cmake_format-format_tests_py3
         COMMAND python3 -m cmake_format.format_tests
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME cmake_format-invocation_tests_py3
         COMMAND python3 -m cmake_format.invocation_tests
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

add_subdirectory(doc)
add_subdirectory(test)
