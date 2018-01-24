# The following multiple newlines should be collapsed into a single newline




cmake_minimum_required(VERSION 2.8.11)
project(cmake_format_test)

# This multiline-comment should be reflowed
# into a single comment
# on one line

# This comment should remain right before the command call.
# Furthermore, the command call should be formatted
# to a single line.
add_subdirectories(foo bar baz
  foo2 bar2 baz2)

# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h very_long_header_name_c.h)

# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES source_a.cc source_b.cc source_d.cc source_e.cc source_f.cc source_g.cc)

# The string in this command should not be split
set_target_properties(foo bar baz PROPERTIES COMPILE_FLAGS "-std=c++11 -Wall -Wextra")

# This command has a very long argument and can't be aligned with the command
# end, so it should be moved to a new line with block indent + 1.
some_long_command_name("Some very long argument that really needs to be on the next line.")

# This situation is similar but the argument to a KWARG needs to be on a
# newline instead.
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-sign-compare -Wno-unused-parameter -xx")

set(HEADERS header_a.h header_b.h # This comment should
                                  # be preserved, moreover it should be split
                                  # across two lines.
    header_c.h header_d.h)


# This part of the comment should
# be formatted
# but...
# cmake-format: off
# This bunny should remain untouched:
# . 　 ＿　∩
# 　　ﾚﾍヽ| |
# 　　　 (・ｘ・)
# 　　 c( uu}
# cmake-format: on
#          while this part should
#          be formatted again

# This is a paragraph
#
# This is a second paragraph
#
# This is a third paragraph

# This is a comment
# that should be joined but
# TODO(josh): This todo should not be joined with the previous line.
# NOTE(josh): Also this should not be joined with the todo.

if(foo)
if(sbar)
# This comment is in-scope.
add_library(foo_bar_baz foo.cc bar.cc # this is a comment for arg2
               # this is more comment for arg2, it should be joined with the first.
    baz.cc) # This comment is part of add_library

other_command(some_long_argument some_long_argument) # this comment is very long and gets split across some lines

other_command(some_long_argument some_long_argument some_long_argument) # this comment is even longer and wouldn't make sense to pack at the end of the command so it gets it's own lines
endif()
endif()


# This very long command should be broken up along keyword arguments
foo(nonkwarg_a nonkwarg_b HEADERS a.h b.h c.h d.h e.h f.h SOURCES a.cc b.cc d.cc DEPENDS foo bar baz)

# This command uses a string with escaped quote chars
foo(some_arg some_arg "This is a \"string\" within a string")

# This command uses an empty string
foo(some_arg some_arg "")

# This command uses a multiline string
foo(some_arg some_arg "
    This string is on multiple lines
")

# No, I really want this to look ugly
# cmake-format: off
add_library(a b.cc
  c.cc         d.cc
           e.cc)
# cmake-format: on
