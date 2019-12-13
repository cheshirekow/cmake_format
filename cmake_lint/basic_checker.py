# pylint: disable=W0613
import enum
import re

from cmake_format.formatter import get_comment_lines
from cmake_format.lexer import TokenType, Token
from cmake_format.parse.argument_nodes import (
    ConditionalGroupNode, PositionalGroupNode
)
from cmake_format.parse.body_nodes import FlowControlNode
from cmake_format.parse.common import NodeType, TreeNode
from cmake_format.parse.statement_node import StatementNode
from cmake_format.parse.util import get_min_npargs


def find_statements_in_subtree(subtree, funnames):
  """
  Return a generator that yields all statements in the `subtree` which match
  the provided set of `funnames`.
  """
  if isinstance(subtree, (list, tuple)):
    queue = subtree
  else:
    queue = [subtree]

  while queue:
    node = queue.pop(0)
    if isinstance(node, StatementNode):
      if node.get_funname() in funnames:
        yield node
    for child in node.children:
      if isinstance(child, TreeNode):
        queue.append(child)


def find_nodes_in_subtree(subtree, nodetypes):
  """Return a generator that yields all nodes in the `subtree` which are of the
     given type(s) `nodetypes`.
  """
  if isinstance(subtree, (list, tuple)):
    queue = subtree
  else:
    queue = [subtree]

  while queue:
    node = queue.pop(0)
    if isinstance(node, nodetypes):
      yield node

    if isinstance(node, TreeNode):
      for child in node.children:
        queue.append(child)


def check_basics(cfg, local_ctx, infile_content):
  """Perform  basic checks before even lexing the file
  """
  lines = infile_content.split("\n")

  for lineno, line in enumerate(lines):
    if len(line) > cfg.line_width:
      local_ctx.record_lint(
          "C0301", len(line), cfg.line_width, location=(lineno,))

    if line.endswith("\r"):
      if cfg.line_ending == "unix":
        local_ctx.record_lint(
            "C0327", "windows", location=(lineno,))
      line = line[:-1]
    else:
      if cfg.line_ending == "windows":
        local_ctx.record_lint(
            "C0327", "unix", location=(lineno,))

    if len(line.rstrip()) != len(line):
      local_ctx.record_lint("C0303", location=(lineno,))

  # check that the file ends with newline
  if not infile_content.endswith("\n"):
    local_ctx.record_lint("C0304", location=(len(lines),))


def loop_contains_argn(loop_stmt):
  """Return true if the loop statement contains ${ARGN} as an argument"""
  for token in loop_stmt.argtree.get_semantic_tokens():
    if token.type is TokenType.DEREF and token.spelling == "${ARGN}":
      return True
  return False


def check_for_custom_parse_logic(cfg, local_ctx, stmt_node):
  """Ensure that a function or macro definition doesn't contain custom parser
     logic. The check is heuristic, but what we look for is a loop over ARGN
     where the body of the loop contains multiple conditional checks against
     the string value of the arguments
  """
  block = stmt_node.parent.get_block_with(stmt_node)
  for _ in find_statements_in_subtree(
      block.body, ("cmake_parse_arguments",)):
    # function/macro definition uses the std parser, so the check is complete
    return

  for loop_stmt in find_statements_in_subtree(block.body, ("foreach", "while")):
    if loop_contains_argn(loop_stmt):
      conditional_count = 0
      loopvar = loop_stmt.argtree.get_semantic_tokens()[0]
      loop_body = loop_stmt.parent.get_block_with(loop_stmt).body
      for conditional in find_nodes_in_subtree(
          loop_body, ConditionalGroupNode):
        tokens = conditional.get_semantic_tokens()
        if not tokens:
          continue
        if tokens[0].spelling == loopvar.spelling:
          if tokens[1].spelling in ("STREQUAL", "MATCHES"):
            conditional_count += 1
      if conditional_count > cfg.linter.max_conditionals_custom_parser:
        local_ctx.record_lint("C0201", location=loop_stmt.get_location())
        return


def check_name_against_pattern(cfg, local_ctx, defn_node, pattern):
  """Check that a function or macro name matches the required pattern."""
  tokens = defn_node.get_semantic_tokens()
  tokens.pop(0)  # statement name "function" or "macro"
  tokens.pop(0)  # lparen

  token = tokens.pop(0)  # function/macro name
  if not re.match(pattern, token.spelling):
    local_ctx.record_lint(
        "C0103", "function", token.spelling, location=token.get_location())


def check_argument_names(cfg, local_ctx, defn_node):
  """Check that the argument names in a function or macro definition match
     the required pattern."""
  tokens = defn_node.argtree.get_semantic_tokens()[1:]
  seen_names = set()
  uncase_names = set()
  for token in tokens:  # named arguments
    if token.type is TokenType.RIGHT_PAREN:
      break
    if token.type is not TokenType.WORD:
      local_ctx.record_lint(
          "E0109", token.spelling, location=token.get_location())
    else:
      if token.spelling in seen_names:
        local_ctx.record_lint(
            "E0108", token.spelling, location=token.get_location())
      elif token.spelling.lower() in uncase_names:
        local_ctx.record_lint(
            "C0202", token.spelling, location=token.get_location())
      elif not re.match(cfg.linter.local_var_pattern, token.spelling):
        local_ctx.record_lint(
            "C0103", "argument", token.spelling, location=token.get_location())
      seen_names.add(token.spelling)
      uncase_names.add(token.spelling.lower())

  if len(tokens) > cfg.linter.max_arguments:
    local_ctx.record_lint("R0913", len(tokens), cfg.linter.max_arguments,
                          location=defn_node.get_location())


def check_defn(cfg, local_ctx, defn_node, name_pattern):
  """Perform checks on a function or macro"""
  check_for_custom_parse_logic(cfg, local_ctx, defn_node)
  check_name_against_pattern(cfg, local_ctx, defn_node, name_pattern)
  check_argument_names(cfg, local_ctx, defn_node)

  block = defn_node.parent.get_block_with(defn_node)
  return_count = sum(
      1 for _ in find_statements_in_subtree(block.body, ("return",)))
  if return_count > cfg.linter.max_returns:
    local_ctx.record_lint("R0911", return_count, cfg.linter.max_returns,
                          location=defn_node.get_location())

  branch_count = sum(
      1 for _ in find_statements_in_subtree(
          block.body, ("if", "elseif", "else")))
  if branch_count > cfg.linter.max_branches:
    local_ctx.record_lint("R0912", branch_count, cfg.linter.max_branches,
                          location=defn_node.get_location())

  stmt_count = sum(
      1 for _ in find_nodes_in_subtree(block.body, StatementNode))
  if stmt_count > cfg.linter.max_statements:
    local_ctx.record_lint("R0915", stmt_count, cfg.linter.max_statements,
                          location=defn_node.get_location())


def check_fundef(cfg, local_ctx, node):
  """Perform checks on a function definition"""
  check_defn(cfg, local_ctx, node, cfg.linter.function_pattern)


def check_macrodef(cfg, local_ctx, node):
  """Perform checks on a macro definition"""
  check_defn(cfg, local_ctx, node, cfg.linter.macro_pattern)


def check_foreach(cfg, local_ctx, node):
  """Perform checks on a foreach statement"""
  tokens = node.get_semantic_tokens()
  tokens.pop(0)  # statement name "foreach"
  tokens.pop(0)  # lparen

  token = tokens.pop(0)  # loopvaraible
  if not re.match(cfg.linter.local_var_pattern, token.spelling):
    local_ctx.record_lint(
        "C0103", "loopvar", token.spelling, location=token.get_location())


def check_flow_control(cfg, local_ctx, node):
  """Perform checks on a flowcontrol node."""
  stmt = node.children[0]
  funname = stmt.children[0].children[0].spelling.lower()
  if funname == "function":
    check_fundef(cfg, local_ctx, stmt)
  elif funname == "macro":
    check_macrodef(cfg, local_ctx, stmt)
  elif funname == "foreach":
    check_foreach(cfg, local_ctx, stmt)
  for child in node.children:
    check_tree(cfg, local_ctx, child)


def parse_pragmas_from_token(local_ctx, content, row, col, supressions):
  """Parse any cmake-lint directives (pragmas) from line-comment
     tokens at the current scope."""
  items = content.split()
  for item in items:
    if "=" not in item:
      local_ctx.record_lint("E0011", item, location=(row, col))
      col += len(item) + 1
      continue

    key, value = item.split("=", 1)
    if key == "disable":
      idlist = value.split(",")
      for idstr in idlist:
        if local_ctx.is_idstr(idstr):
          supressions.append(idstr)
        else:
          local_ctx.record_lint(
              "E0012", idstr, location=(row, col))

    else:
      local_ctx.record_lint(
          "E0011", key, location=(row, col))


def parse_pragmas_from_comment(local_ctx, node):
  """Parse any cmake-lint directives (pragmas) from line comment tokens within
     the comment node."""
  supressions = []
  for child in node.children:
    if not isinstance(child, Token):
      continue
    if child.type is not TokenType.COMMENT:
      continue
    token = child
    pragma_prefix = "# cmake-lint: "
    if not token.spelling.startswith(pragma_prefix):
      continue

    row, col, _ = token.get_location()
    content = token.spelling[len(pragma_prefix):]
    col += len(pragma_prefix)
    parse_pragmas_from_token(local_ctx, content, row, col, supressions)

  return supressions


def statement_is_fundef(node):
  """Return true if a statement node is for a function or macro definition.
  """
  tokens = node.get_semantic_tokens()
  if not tokens:
    return False
  funname = tokens[0].spelling.lower()
  return funname in ("function", "macro")


def get_prefix_comment(prevchild):
  """
  Expect a sequence of COMMENT, WHITESPACE, <node>. If this sequence is true,
  return the comment node.
  """
  for idx in range(2):
    if not isinstance(prevchild[idx], TreeNode):
      return None
  if not prevchild[0].node_type is NodeType.WHITESPACE:
    return None

  newline_count = 0
  for token in prevchild[0].get_tokens():
    newline_count += token.spelling.count("\n")
  if newline_count > 1:
    return None

  if not prevchild[1].node_type is NodeType.COMMENT:
    return None
  return prevchild[1]


def check_body(cfg, local_ctx, node):
  """Perform checks on a body node."""
  supressions = []
  prevchild = [None, None]
  for idx, child in enumerate(node.children):
    if not isinstance(child, TreeNode):
      # Should not be the case. Should we assert here?
      continue

    if child.node_type is NodeType.COMMENT:
      requested_supressions = parse_pragmas_from_comment(local_ctx, child)
      if requested_supressions:
        new_supressions = local_ctx.supress(requested_supressions)
        supressions.extend(new_supressions)

    # Check for docstrings
    # TODO(josh): move into flow-control or fundef/macrodef checkers? Would
    # require an API to get siblings
    if child.node_type is NodeType.FLOW_CONTROL:
      stmt = child.children[0]
      if statement_is_fundef(stmt):
        prefix_comment = get_prefix_comment(prevchild)
        if not prefix_comment:
          local_ctx.record_lint(
              "C0111", location=child.get_semantic_tokens()[0].get_location())
        elif not "".join(get_comment_lines(cfg, prefix_comment)).strip():
          local_ctx.record_lint(
              "C0112", location=child.get_semantic_tokens()[0].get_location())

    # Check spacing between statements at block level
    # TODO(josh): move into flow-control and statement checkers? Would
    # require an API to get siblings
    if child.node_type in (NodeType.FLOW_CONTROL, NodeType.STATEMENT):
      if prevchild[0] is None:
        pass
      elif prevchild[0].node_type is not NodeType.WHITESPACE:
        local_ctx.record_lint("C0321", location=child.get_location())
      elif prevchild[0].count_newlines() < 1:
        local_ctx.record_lint("C0321", location=child.get_location())
      elif prevchild[0].count_newlines() < cfg.linter.min_statement_spacing:
        local_ctx.record_lint(
            "C0305", "not enough", location=child.get_location())
      elif prevchild[0].count_newlines() > cfg.linter.max_statement_spacing:
        local_ctx.record_lint(
            "C0305", "too many", location=child.get_location())

    if (isinstance(child, StatementNode) and
        child.get_funname() in ("break", "continue", "return")):
      for _ in find_nodes_in_subtree(node.children[idx + 1:], StatementNode):
        local_ctx.record_lint("W0101", location=child.get_location())
        break

    check_tree(cfg, local_ctx, child)
    prevchild[1] = prevchild[0]
    prevchild[0] = child
  local_ctx.unsupress(supressions)


def check_arggroup(cfg, local_ctx, node):
  kwargs_seen = set()
  for child in node.children:
    if isinstance(child, TreeNode) and child.node_type is NodeType.KWARGGROUP:
      kwarg_token = child.get_semantic_tokens()[0]
      kwarg = kwarg_token.spelling.upper()
      if kwarg in ("AND", "OR", "COMMAND"):
        continue
      if kwarg in kwargs_seen:
        local_ctx.record_lint(
            "E1122", kwarg, location=kwarg_token.get_location())
      kwargs_seen.add(kwarg)
    check_tree(cfg, local_ctx, child)


def check_positional_group(cfg, local_ctx, node):
  """Perform checks on a positinal group node."""
  min_npargs = get_min_npargs(node.spec.npargs)
  semantic_tokens = node.get_semantic_tokens()
  if len(semantic_tokens) < min_npargs:
    location = ()
    if semantic_tokens:
      location = semantic_tokens[0].get_location()
    local_ctx.record_lint("E1120", location=location)


def check_is_in_loop(cfg, local_ctx, node):
  """Ensure that a break() or continue() statement has a foreach() or
     while() node in it's ancestry."""
  parent = node.parent

  while parent:
    if not isinstance(parent, FlowControlNode):
      parent = parent.parent
      continue

    block = parent.get_block_with(node)
    if block is None:
      parent = parent.parent
      continue

    if block.open_stmt.get_funname() in ("foreach", "while"):
      return True

    parent = parent.parent
  local_ctx.record_lint(
      "E0103", node.get_funname(), location=node.get_location())


class Scope(enum.IntEnum):
  CACHE = 0  # global scope (public)
  INTERNAL = 1  # global scope (private)
  PARENT = 1  # indeterminate scope, but it can't be CACHE
  LOCAL = 2  # function local scope
  DIRECTORY = 3  # directory scope


def get_scope_of_assignment(set_node):
  """Return the scope of the assignment."""
  args = set_node.argtree
  if args.cache:
    if args.cache.type == "INTERNAL":
      return Scope.INTERNAL
    return Scope.CACHE

  if args.parent_scope:
    return Scope.PARENT

  # assume block (directory) scope
  prev = set_node
  parent = args.parent
  while parent:
    if isinstance(parent, FlowControlNode):
      block = parent.get_block_with(prev)
      if block.open_stmt.get_funname() == "function":
        # found ourselves in the body of a function, which means that we are
        # local scope
        return Scope.LOCAL
      if block.open_stmt.get_funname() == "macro":
        # found ourselves in the body of a macro, which means that we are
        # in parent scope
        return Scope.PARENT
    prev = parent
    parent = parent.parent
  return Scope.DIRECTORY


def check_assignment(cfg, local_ctx, set_node):
  """Checks on a variable assignment."""
  scope = get_scope_of_assignment(set_node)
  varname = set_node.argtree.varname

  if scope is Scope.CACHE:
    # variable is global scope and public
    pattern = cfg.linter.global_var_pattern
    if not re.match(pattern, varname.spelling):
      local_ctx.record_lint(
          "C0103", "CACHE variable", varname.spelling,
          location=varname.get_location())
  elif scope is Scope.INTERNAL:
    # variable is global scope but private
    pattern = cfg.linter.internal_var_pattern
    if not re.match(pattern, varname.spelling):
      local_ctx.record_lint(
          "C0103", "INTERNAL variable", varname.spelling,
          location=varname.get_location())
  elif scope is Scope.PARENT:
    # indeterminate scope, but it's not global
    pattern = "|".join([
        cfg.linter.public_var_pattern,
        cfg.linter.private_var_pattern,
        cfg.linter.local_var_pattern,
    ])

    if not re.match(pattern, varname.spelling):
      local_ctx.record_lint(
          "C0103", "PARENT_SCOPE variable", varname.spelling,
          location=varname.get_location())
  elif scope is Scope.LOCAL:
    if not re.match(cfg.linter.local_var_pattern, varname.spelling):
      local_ctx.record_lint(
          "C0103", "local variable", varname.spelling,
          location=varname.get_location())
  elif scope is Scope.DIRECTORY:
    # We cannot tell by assignment whether it's meant to be public or private,
    # but it must match one of these patterns
    pattern = "|".join([
        cfg.linter.public_var_pattern,
        cfg.linter.private_var_pattern,
    ])
    if not re.match(pattern, varname.spelling):
      local_ctx.record_lint(
          "C0103", "directory variable", varname.spelling,
          location=varname.get_location())


def check_statement(cfg, local_ctx, node):
  """Perform checks on a statement."""
  if node.get_funname() in ("break", "continue"):
    check_is_in_loop(cfg, local_ctx, node)
  elif node.get_funname() == "set":
    check_assignment(cfg, local_ctx, node)
  for child in node.children:
    check_tree(cfg, local_ctx, child)


def check_tree(cfg, local_ctx, node):
  if not isinstance(node, TreeNode):
    return
  if node.node_type is NodeType.BODY:
    check_body(cfg, local_ctx, node)
  elif node.node_type is NodeType.FLOW_CONTROL:
    check_flow_control(cfg, local_ctx, node)
  elif node.node_type is NodeType.ARGGROUP:
    check_arggroup(cfg, local_ctx, node)
  elif isinstance(node, StatementNode):
    check_statement(cfg, local_ctx, node)
  elif isinstance(node, PositionalGroupNode):
    check_positional_group(cfg, local_ctx, node)
  else:
    for child in node.children:
      check_tree(cfg, local_ctx, child)
