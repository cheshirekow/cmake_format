import logging

from cmake_format import lexer
from cmake_format.parser import (
    NodeType,
    get_first_semantic_token,
    get_normalized_kwarg,
    KwargBreaker,
    parse_flags,
    parse_kwarg,
    parse_positionals,
    parse_standard,
    parse_shell_command,
    PositionalParser,
    PositionalTupleParser,
    should_break,
    TreeNode,
    WHITESPACE_TOKENS
)

logger = logging.getLogger("cmake-format")


def parse_add_custom_command_events(tokens, breakstack):
  """
  ::
    add_custom_command(TARGET <target>
                    PRE_BUILD | PRE_LINK | POST_BUILD
                    COMMAND command1 [ARGS] [args1...]
                    [COMMAND command2 [ARGS] [args2...] ...]
                    [BYPRODUCTS [files...]]
                    [WORKING_DIRECTORY dir]
                    [COMMENT comment]
                    [VERBATIM] [USES_TERMINAL]
                    [COMMAND_EXPAND_LISTS])
  :see: https://cmake.org/cmake/help/latest/command/add_custom_command.html
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "BYPRODUCTS": PositionalParser('*'),
          "COMMAND": parse_shell_command,
          "COMMENT": PositionalParser('*'),
          "TARGET": PositionalParser(1),
          "WORKING_DIRECTORY": PositionalParser(1)
      },
      flags=[
          "APPEND", "VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS",
          "PRE_BUILD", "PRE_LINK", "POST_BUILD"],
      breakstack=breakstack)


def parse_add_custom_command_standard(tokens, breakstack):
  """
  ::

      add_custom_command(OUTPUT output1 [output2 ...]
                         COMMAND command1 [ARGS] [args1...]
                         [COMMAND command2 [ARGS] [args2...] ...]
                         [MAIN_DEPENDENCY depend]
                         [DEPENDS [depends...]]
                         [BYPRODUCTS [files...]]
                         [IMPLICIT_DEPENDS <lang1> depend1
                                          [<lang2> depend2] ...]
                         [WORKING_DIRECTORY dir]
                         [COMMENT comment]
                         [DEPFILE depfile]
                         [JOB_POOL job_pool]
                         [VERBATIM] [APPEND] [USES_TERMINAL]
                         [COMMAND_EXPAND_LISTS])

  :see: https://cmake.org/cmake/help/latest/command/add_custom_command.html
  """
  return parse_standard(
      tokens,
      npargs='*',
      kwargs={
          "BYPRODUCTS": PositionalParser('*'),
          "COMMAND": parse_shell_command,
          "COMMENT": PositionalParser('*'),
          "DEPENDS": PositionalParser('*'),
          "DEPFILE": PositionalParser(1),
          "JOB_POOL": PositionalParser(1),
          "IMPLICIT_DEPENDS": PositionalTupleParser(2, '+'),
          "MAIN_DEPENDENCY": PositionalParser(1),
          "OUTPUT": PositionalParser('+'),
          "WORKING_DIRECTORY": PositionalParser(1)
      },
      flags=["APPEND", "VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"],
      breakstack=breakstack)


def parse_add_custom_command(tokens, breakstack):
  """
  There are two forms of `add_custom_command`. This is the dispatcher between
  the two forms.
  """
  descriminator_token = get_first_semantic_token(tokens)
  descriminator_word = get_normalized_kwarg(descriminator_token)
  if descriminator_word == "TARGET":
    return parse_add_custom_command_events(tokens, breakstack)
  if descriminator_word == "OUTPUT":
    return parse_add_custom_command_standard(tokens, breakstack)

  logger.warning(
      "Indeterminate form of add_custom_command at %s",
      descriminator_token.location)
  return parse_add_custom_command_standard(tokens, breakstack)


def parse_add_custom_target(tokens, breakstack):
  """
  ::
    add_custom_target(Name [ALL] [command1 [args1...]]
                      [COMMAND command2 [args2...] ...]
                      [DEPENDS depend depend depend ... ]
                      [BYPRODUCTS [files...]]
                      [WORKING_DIRECTORY dir]
                      [COMMENT comment]
                      [JOB_POOL job_pool]
                      [VERBATIM] [USES_TERMINAL]
                      [COMMAND_EXPAND_LISTS]
                      [SOURCES src1 [src2...]])

  :see: https://cmake.org/cmake/help/latest/command/add_custom_target.html
  """
  kwargs = {
      "BYPRODUCTS": PositionalParser("+"),
      "COMMAND": parse_shell_command,
      "COMMENT": PositionalParser(1),
      "DEPENDS": PositionalParser("+"),
      "JOB_POOL": PositionalParser(1),
      "SOURCES": PositionalParser("+"),
      "WORKING_DIRECTORY": PositionalParser(1),
  }
  flags = ("VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS")
  tree = TreeNode(NodeType.ARGGROUP)

  # If it is a whitespace token then put it directly in the parse tree at
  # the current depth
  while tokens and tokens[0].type in WHITESPACE_TOKENS:
    tree.children.append(tokens.pop(0))
    continue

  breaker = KwargBreaker(list(kwargs.keys()) + list(flags))
  child_breakstack = breakstack + [breaker]

  nametree = None
  state = "name"

  while tokens:
    # Break if the next token belongs to a parent parser, i.e. if it
    # matches a keyword argument of something higher in the stack, or if
    # it closes a parent group.
    if should_break(tokens[0], breakstack):
      break

    # If it is a whitespace token then put it directly in the parse tree at
    # the current depth
    if tokens[0].type in WHITESPACE_TOKENS:
      tree.children.append(tokens.pop(0))
      continue

    # If it's a comment, then add it at the current depth
    if tokens[0].type in (lexer.TokenType.COMMENT,
                          lexer.TokenType.BRACKET_COMMENT):
      child = TreeNode(NodeType.COMMENT)
      tree.children.append(child)
      child.children.append(tokens.pop(0))
      continue

    ntokens = len(tokens)
    if state == "name":
      next_semantic = get_first_semantic_token(tokens[1:])
      if (next_semantic is not None and
          get_normalized_kwarg(next_semantic) == "ALL"):
        npargs = 2
      else:
        npargs = 1

      nametree = parse_positionals(tokens, npargs, ["ALL"], child_breakstack)
      assert len(tokens) < ntokens
      tree.children.append(nametree)
      state = "first-command"
      continue

    word = get_normalized_kwarg(tokens[0])
    if state == "first-command":
      if not(word in kwargs or word in flags):
        subtree = parse_positionals(tokens, '+', [], child_breakstack)
        tree.children.append(subtree)
        assert len(tokens) < ntokens
      state = "kwargs"
      continue

    if word in flags:
      subtree = parse_flags(
          tokens, flags, breakstack + [KwargBreaker(list(kwargs.keys()))])
      assert len(tokens) < ntokens
      tree.children.append(subtree)
      continue

    if word in kwargs:
      subtree = parse_kwarg(tokens, word, kwargs[word], child_breakstack)
      assert len(tokens) < ntokens
      tree.children.append(subtree)
      continue

    logger.warning(
        "Unexpected positional argument %s at %s",
        tokens[0].spelling, tokens[0].location())
    subtree = parse_positionals(tokens, '+', [], child_breakstack)
    assert len(tokens) < ntokens
    tree.children.append(subtree)
    continue
  return tree


def populate_db(parse_db):
  parse_db["add_custom_command"] = parse_add_custom_command
  parse_db["add_custom_target"] = parse_add_custom_target
