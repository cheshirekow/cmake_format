# How wide to allow formatted cmake files
line_width = 80

# How many spaces to tab for indent (overridden by cmake-format-split2.py)
tab_size = 10

# If arglists are longer than this, break them always.
max_subargs_per_line = 3

# If true, separate control flow names from the parentheses with a space
separate_ctrl_name_with_space = False

# If true, separate function names from the parenthesis with a space
separate_fn_name_with_space = False

# Additional FLAGS and KWARGS for custom commands
# (extended by cmake-format-split2.py)
additional_commands = {
  "foo": {
    "flags": ["BAR", "BAZ"],
  }
}
