# pylint: disable=invalid-name
# How wide to allow formatted cmake files
line_width = 80

# How many spaces to tab for indent
tab_size = 2

# If arglists are longer than this, break them always.
max_subargs_per_line = 3

# If true, separate control flow names from the parentheses with a space
separate_ctrl_name_with_space = False

# If true, separate function names from the parenthesis with a space
separate_fn_name_with_space = False

# Additional FLAGS and KWARGS for custom commands
additional_commands = {
    "foo": {
        "flags": ["BAR", "BAZ"],
        "kwargs": {
            "HEADERS": '*',
            "SOURCES": '*',
            "DEPENDS": '*',
        }
    }
}
