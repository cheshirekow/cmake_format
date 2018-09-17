format_and_lint(cmake_format
                __init__.py
                __main__.py
                commands.py
                common.py
                configuration.py
                format_tests.py
                formatter.py
                invocation_tests.py
                lexer_tests.py
                lexer.py
                markup_tests.py
                markup.py
                parser_tests.py
                parser.py
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

add_subdirectory(doc)
add_subdirectory(test)
