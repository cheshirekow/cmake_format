from cmake_format import lexer
from cmake_format import parser
from cmake_format.parser import (
    consume_trailing_comment,
    get_normalized_kwarg,
    get_tag,
    NodeType,
    only_comments_and_whitespace_remain,
    parse_standard,
    TreeNode,
    WHITESPACE_TOKENS,
)


def parse_add_custom_command(tokens, breakstack):
  """
  ::

    add_custom_command(OUTPUT output1 [output2 ...]
                       COMMAND command1 [ARGS] [args1...]
                       [COMMAND command2 [ARGS] [args2...] ...]
                       [MAIN_DEPENDENCY depend]
                       [DEPENDS [depends...]]
                       [IMPLICIT_DEPENDS <lang1> depend1
                                        [<lang2> depend2] ...]
                       [WORKING_DIRECTORY dir]
                       [COMMENT comment] [VERBATIM] [APPEND])

  :see: https://cmake.org/cmake/help/v3.0/command/add_custom_command.html
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "COMMAND": parser.parse_shell_command,
          "COMMENT": parser.PositionalParser('*'),
          "DEPENDS": parser.PositionalParser('*'),
          "IMPLICIT_DEPENDS": parser.PositionalTupleParser('+', 2),
          "MAIN_DEPENDENCY": parser.PositionalParser(1),
          "OUTPUT": parser.PositionalParser('+'),
          "WORKING_DIRECTORY": parser.PositionalParser(1)
      },
      flags=["APPEND", "VERBATIM",
             "PRE_BUILD", "PRE_LINK", "POST_BUILD"],
      breakstack=breakstack)


def parse_add_executable(tokens, breakstack):
  """
  ::

    add_executable(<name> [WIN32] [MACOSX_BUNDLE]
               [EXCLUDE_FROM_ALL]
               [source1] [source2 ...])

  :see: https://cmake.org/cmake/help/latest/command/add_executable.html#command:add_executable
  """
  # pylint: disable=too-many-statements

  parsing_name = 1
  parsing_flags = 2
  parsing_sources = 3

  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  sortable = True
  state_ = parsing_name
  parg_group = None
  src_group = None
  active_depth = tree

  while tokens:
    # This parse function breaks on the first right paren, since parenthetical
    # groups are not allowed. A parenthesis might exist in a filename, but
    # if so that filename should be quoted so it wont show up as a RIGHT_PAREN
    # token.
    if tokens[0].type is lexer.TokenType.RIGHT_PAREN:
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      active_depth.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      if (state_ > parsing_name and
          get_tag(tokens[0]) in ("unsort", "unsortable")):
        sortable = False
      child = TreeNode(NodeType.COMMENT)
      active_depth.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    if state_ is parsing_name:
      token = tokens.pop(0)
      parg_group = TreeNode(NodeType.PARGGROUP)
      active_depth = parg_group
      tree.children.append(parg_group)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_flags:
      if get_normalized_kwarg(tokens[0]) in (
          "WIN32", "MACOSX_BUNDLE", "EXCLUDE_FROM_ALL"):
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      else:
        state_ += 1
        src_group = TreeNode(NodeType.PARGGROUP, sortable=sortable)
        active_depth = src_group
        tree.children.append(src_group)
    elif state_ is parsing_sources:
      token = tokens.pop(0)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      src_group.children.append(child)

      if only_comments_and_whitespace_remain(tokens, breakstack):
        active_depth = tree

  return tree


def parse_add_library(tokens, breakstack):
  """
  ::

    add_library(<name> [STATIC | SHARED | MODULE]
               [EXCLUDE_FROM_ALL]
               source1 [source2 ...])

  :see: https://cmake.org/cmake/help/v3.0/command/add_library.html
  """
  # pylint: disable=too-many-statements

  parsing_name = 1
  parsing_type = 2
  parsing_flag = 3
  parsing_sources = 4

  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  sortable = True
  state_ = parsing_name
  parg_group = None
  src_group = None
  active_depth = tree

  while tokens:
    # This parse function breakson the first right paren, since parenthetical
    # groups are not allowed. A parenthesis might exist in a filename, but
    # if so that filename should be quoted so it wont show up as a RIGHT_PAREN
    # token.
    if tokens[0].type is lexer.TokenType.RIGHT_PAREN:
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      active_depth.children.append(tokens.pop(0))
      continue

    # If it's a comment token not associated with an argument, then put it
    # directly into the parse tree at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      if (state_ > parsing_name and
          get_tag(tokens[0]) in ("unsort", "unsortable")):
        sortable = False
      child = TreeNode(NodeType.COMMENT)
      active_depth.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    if state_ is parsing_name:
      token = tokens.pop(0)
      parg_group = TreeNode(NodeType.PARGGROUP)
      active_depth = parg_group
      tree.children.append(parg_group)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_type:
      if get_normalized_kwarg(tokens[0]) in ("STATIC", "SHARED", "MODULE"):
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      state_ += 1
    elif state_ is parsing_flag:
      if get_normalized_kwarg(tokens[0]) == "EXCLUDE_FROM_ALL":
        token = tokens.pop(0)
        child = TreeNode(NodeType.FLAG)
        child.children.append(token)
        consume_trailing_comment(child, tokens)
        parg_group.children.append(child)
      state_ += 1
      src_group = TreeNode(NodeType.PARGGROUP, sortable=sortable)
      active_depth = src_group
      tree.children.append(src_group)
    elif state_ is parsing_sources:
      token = tokens.pop(0)
      child = TreeNode(NodeType.ARGUMENT)
      child.children.append(token)
      consume_trailing_comment(child, tokens)
      src_group.children.append(child)

      if only_comments_and_whitespace_remain(tokens, breakstack):
        active_depth = tree

  return tree


def populate_db(parse_db):
  parse_db["add_custom_command"] = parse_add_custom_command
  parse_db["add_executable"] = parse_add_executable
  parse_db["add_library"] = parse_add_library
