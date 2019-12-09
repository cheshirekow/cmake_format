import re

from cmake_format.lexer import TokenType, Token
from cmake_format.parser import NodeType, TreeNode
from cmake_format.formatter import get_comment_lines


def check_basics(cfg, local_ctx, infile_content):
  """
  Perform  basic checks before even lexing the file
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


def check_function_decl(cfg, local_ctx, node):
  tokens = node.get_semantic_tokens()
  tokens.pop(0)  # statement name "function"
  tokens.pop(0)  # lparen

  token = tokens.pop(0)  # function name
  if not re.match(cfg.linter.function_pattern, token.spelling):
    local_ctx.record_lint(
        "C0103", "function", token.spelling, location=token.get_location())

  for token in tokens:  # named arguments
    if token.type is TokenType.RIGHT_PAREN:
      break
    if not re.match(cfg.linter.local_var_pattern, token.spelling):
      local_ctx.record_lint(
          "C0103", "argument", token.spelling, location=token.get_location())


def check_macro_decl(cfg, local_ctx, node):
  tokens = node.get_semantic_tokens()
  tokens.pop(0)  # statement name "function"
  tokens.pop(0)  # lparen

  token = tokens.pop(0)  # function name
  if not re.match(cfg.linter.macro_pattern, token.spelling):
    local_ctx.record_lint(
        "C0103", "function", token.spelling, location=token.get_location())

  for token in tokens:  # named arguments
    if token.type is TokenType.RIGHT_PAREN:
      break
    if not re.match(cfg.linter.local_var_pattern, token.spelling):
      local_ctx.record_lint(
          "C0103", "argument", token.spelling, location=token.get_location())


def check_foreach(cfg, local_ctx, node):
  tokens = node.get_semantic_tokens()
  tokens.pop(0)  # statement name "foreach"
  tokens.pop(0)  # lparen

  token = tokens.pop(0)  # loopvaraible
  if not re.match(cfg.linter.local_var_pattern, token.spelling):
    local_ctx.record_lint(
        "C0103", "loopvar", token.spelling, location=token.get_location())


def check_flow_control(cfg, local_ctx, node):
  stmt = node.children[0]
  funname = stmt.children[0].children[0].spelling.lower()
  if funname == "function":
    check_function_decl(cfg, local_ctx, stmt)
  elif funname == "macro":
    check_macro_decl(cfg, local_ctx, stmt)
  elif funname == "foreach":
    check_foreach(cfg, local_ctx, stmt)
  for child in node.children:
    check_tree(cfg, local_ctx, child)


def parse_pragmas_from_token(local_ctx, content, row, col, supressions):

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
  """
  Return true if a statement node is for a function or macro definition.
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
  supressions = []
  prevchild = [None, None]
  for child in node.children:
    if isinstance(child, TreeNode) and child.node_type is NodeType.COMMENT:
      requested_supressions = parse_pragmas_from_comment(local_ctx, child)
      if requested_supressions:
        new_supressions = local_ctx.supress(requested_supressions)
        supressions.extend(new_supressions)
    elif (isinstance(child, TreeNode) and
          child.node_type is NodeType.FLOW_CONTROL):
      stmt = child.children[0]
      if statement_is_fundef(stmt):
        prefix_comment = get_prefix_comment(prevchild)
        if not prefix_comment:
          local_ctx.record_lint(
              "C0111", location=child.get_semantic_tokens()[0].get_location())
        elif not "".join(get_comment_lines(cfg, prefix_comment)).strip():
          local_ctx.record_lint(
              "C0112", location=child.get_semantic_tokens()[0].get_location())

    check_tree(cfg, local_ctx, child)
    prevchild[1] = prevchild[0]
    prevchild[0] = child
  local_ctx.unsupress(supressions)


def check_tree(cfg, local_ctx, node):
  if not isinstance(node, TreeNode):
    return
  if node.node_type is NodeType.BODY:
    check_body(cfg, local_ctx, node)
  elif node.node_type is NodeType.FLOW_CONTROL:
    check_flow_control(cfg, local_ctx, node)
  else:
    for child in node.children:
      check_tree(cfg, local_ctx, child)
