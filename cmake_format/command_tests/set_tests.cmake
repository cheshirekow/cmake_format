# test: parse
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.PARGGROUP, [
          (NodeType.ARGUMENT, []),
        ]),
        (NodeType.PARGGROUP, [
          (NodeType.COMMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
          (NodeType.ARGUMENT, []),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)

# test: tag_ignored_if_autosort_disabled
#[=[
autosort = False
]=]
set(SOURCES #[[cmf:sortable]] foo.cc bar.cc baz.cc)

# test: tag_respected_if_autosort_enabled
#[=[
autosort = True
]=]
set(SOURCES #[[cmf:sortable]] bar.cc baz.cc foo.cc)

# test: bracket_comment_is_not_trailing_comment_of_kwarg
#[=[
autosort = True
]=]
set(SOURCES #[[cmf:sortable]] #
            bar.cc baz.cc foo.cc)

# test: bracket_commet_short_tag
#[=[
autosort = True
]=]
set(SOURCES #[[cmf:sort]] bar.cc baz.cc foo.cc)

# test: line_comment_long_tag
#[=[
autosort = True
]=]
set(sources # cmake-format: sortable
            bar.cc baz.cc foo.cc)

# test: long_args_command_split
# This very long command should be split to multiple lines
set(HEADERS very_long_header_name_a.h very_long_header_name_b.h
            very_long_header_name_c.h)

# test: lots_of_args_command_split
# This command should be split into one line per entry because it has a long
# argument list.
set(SOURCES
    source_a.cc
    source_b.cc
    source_d.cc
    source_e.cc
    source_f.cc
    source_g.cc
    source_h.cc)
