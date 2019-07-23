# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines

from __future__ import print_function
from __future__ import unicode_literals
import io
import logging
import re
import sys

from cmake_format import common
from cmake_format import lexer
from cmake_format import markup
from cmake_format import parser

from cmake_format.lexer import TokenType
from cmake_format.parser import FlowType, NodeType

logger = logging.getLogger(__name__)

BLOCK_TYPES = (NodeType.FLOW_CONTROL, NodeType.BODY, NodeType.COMMENT,
               NodeType.STATEMENT, NodeType.WHITESPACE, NodeType.ONOFFSWITCH)
GROUP_TYPES = (NodeType.ARGGROUP, NodeType.KWARGGROUP, NodeType.PARGGROUP,
               NodeType.FLAGGROUP, NodeType.PARENGROUP)
SCALAR_TYPES = (NodeType.FUNNAME, NodeType.ARGUMENT, NodeType.KEYWORD,
                NodeType.FLAG)
PAREN_TYPES = (NodeType.LPAREN, NodeType.RPAREN)

MATCH_TYPES = BLOCK_TYPES + GROUP_TYPES + SCALAR_TYPES + PAREN_TYPES

LAYOUT_PASS_COUNT = 4
USE_NEW_ALGORITHM = False


def clamp(value, min_value, max_value):
  """Simple double-ended saturation function."""
  if value > max_value:
    return max_value
  if value < min_value:
    return min_value
  return value


def format_comment_lines(node, config, line_width):
  """
  Reflow comment lines into the given line width, parsing markup as necessary.
  """
  inlines = []
  for token in node.children:
    assert isinstance(token, lexer.Token)
    if token.type == TokenType.COMMENT:
      inline = token.spelling.strip()

      if not config.enable_markup:
        # If markup processing is disabled, preserve the entire line regardless
        # of content
        inlines.append(inline[1:])
      elif inline.startswith('#' * config.hashruler_min_length):
        # If the comment starts with multiple hash chars and it is long enough
        # then treat it as a ruler and preserve it.
        inlines.append(inline[1:])
      else:
        # Otherwise strip off extra hash chars to keep things nice and
        # consistent (i.e. remove acciental `##`` prefixes)
        inlines.append(inline.lstrip('#'))

  if not config.enable_markup:
    return ["#" + line.rstrip() for line in inlines]

  if config.literal_comment_pattern is not None:
    literal_comment_regex = re.compile(config.literal_comment_pattern)
    if literal_comment_regex.match('\n'.join(inlines)):
      return ["#" + line.rstrip() for line in inlines]

  if node.children[0] is config.first_token and (
      config.first_comment_is_literal
      or config.first_token.spelling.startswith("#!")):
    return ["#" + line.rstrip() for line in inlines]

  items = markup.parse(inlines, config)
  markup_lines = markup.format_items(config, max(10, line_width - 2), items)
  return ["#" + (" " * len(line[:1])) + line for line in markup_lines]


def normalize_line_endings(instr):
  """
  Remove trailing whitespace and replace line endings with unix line endings.
  They will be replaced with config.endl during output
  """
  return re.sub('[ \t\f\v]*((\r?\n)|(\r\n?))', '\n', instr)


# TODO(josh): remove this
class WrapAlgo(common.EnumObject):
  """
  Packing algorithm used
  """
  _id_map = {}


WrapAlgo.HPACK = WrapAlgo(0)  # Horizontal packing: no wrapping
WrapAlgo.HWRAP = WrapAlgo(1)  # Horizontal wrapping
WrapAlgo.VPACK = WrapAlgo(2)  # Vertical packing: each element on it's own line
WrapAlgo.KWNVPACK = WrapAlgo(3)  # keyword nested vertical packing
WrapAlgo.PNVPACK = WrapAlgo(4)  # parentheses nested vertical packing
WrapAlgo.COUNT = WrapAlgo(5)


def need_paren_space(spelling, config):
  """
  Return whether or not we need a space between the statement name and the
  starting parenthesis. This aggregates the logic of the two configuration
  options `separate_ctrl_name_with_space` and `separate_fn_name_with_space`.
  """
  upper = spelling.upper()

  if FlowType.get(upper) is not None:
    return config.separate_ctrl_name_with_space
  if upper.startswith('END') and FlowType.get(upper[3:]) is not None:
    return config.separate_ctrl_name_with_space
  if upper in ["ELSE", "ELSEIF"]:
    return config.separate_ctrl_name_with_space

  return config.separate_fn_name_with_space


class Cursor(object):
  """
  Lightweight class to encode integer positions in a 2d grid.

  * x = row
  * y = cols
  """

  def __init__(self, x, y):
    self.x = x  # row
    self.y = y  # col

  def __add__(self, other):
    return Cursor(self.x + other[0], self.y + other[1])

  def __sub__(self, other):
    return Cursor(self.x - other[0], self.y - other[1])

  def __getitem__(self, idx):
    if idx == 0:
      return self.x
    if idx == 1:
      return self.y

    raise IndexError('Cursor indices must be 0 or 1')

  def __setitem__(self, idx, value):
    if idx == 0:
      self.x = value
      return
    if idx == 1:
      self.y = value
      return

    raise IndexError('Cursor indices must be 0 or 1')

  def __repr__(self):
    return "Cursor({},{})".format(self.x, self.y)


def default_accept_layout(
    config, node_path, nested, vertical, start_extent, end_extent):
  """
  Return true if the given layout is acceptable.
  """

  # If the bounding box overflows the column limit then the layout is
  # automatically voided
  if end_extent[1] > config.linewidth:
    return False

  # Commands are never wrapped vertically
  if node_path[-1] == "COMMAND":
    if vertical:
      return False

  size = end_extent - start_extent
  depth = len(node_path) - 1

  prefix_width = len(node_path[-1])
  if depth == 0:
    # If depth is zero, then we are at statement-depth, and we need to account
    # for extra characters when determining the width of the prefix
    prefix_width += 1  # For the left-paren
    if need_paren_space(node_path[-1], config):
      prefix_width += 1  # For the space before the paren

  if not vertical:
    # Regardless of nesting, if the content is wrapped horizontally but it
    # exceeds the configured maximum number of lines we must reject it
    # TODO(josh): figure out how to subtract out any terminal comment
    # contributions to the size, as noted in the algorithm doc.
    if size[0] > config.max_lines_hwrap:
      return False

    # Or if this nodepath is marked to always be vertical layout
    pathstr = "/".join(node_path)
    if pathstr in config.always_wrap:
      return False

  if nested:
    # If the statement or keyword spelling is too short, then nesting doesn't
    # make sense because (nest + tab-width) will take us right back to the
    # same column as without nesting.
    if prefix_width <= config.tab_size:
      return False
  else:
    # If the statement or keyword spelling is too long, then any wrapping also
    # requires nesting.
    if size[0] > 1:
      if prefix_width - config.tab_size > config.max_prefix_chars:
        return False

  return True


def get_nest_wrap(passno):
  """
  Return (nest, wrap) booleans depending on the integer passno
  """
  if passno > 3:
    logger.warning("Invalid passno: %d", passno)
    passno = 3
    # raise ValueError("Invalid passno: {}".format(passno))
  return [
      (False, False),
      (False, True),
      (True, False),
      (True, True)
  ][passno]


class LayoutNode(object):
  """
  An element in the format/layout tree. The structure of the layout tree
  mirrors that of the parse tree. We could store this info the nodes of the
  parse tree itself but it's a little cleaner to keep the functionality
  separate I think.
  """

  def __init__(self, pnode):
    self.pnode = pnode
    self._wrap = WrapAlgo.HPACK
    self._position = Cursor(0, 0)  # NOTE(josh): (row, col)
    self._size = Cursor(0, 0)      # NOTE(josh): (rows, cols)

    # If false, reflow was aborted due to algorithmic constraint: e.g.
    # attempt to horiziontally pack a non-bracket comment, which is
    # syntatically invalid.
    self._reflow_valid = False

    # Set to true if this node is the final node of a statement at
    # the current depth
    self.statement_terminal = False

    self._children = []
    self._passno = -1

    # The first column past the last column covered by this node. This is
    # different than just "position" + "size" in the case that the node
    # contains multiline string or bracket arguments
    self._colextent = 0

    # Depth of this node in the subtree starting at the statement node.
    # If this node is not in a statement subtree the value is zero.
    self._stmt_depth = 0

    # Depth of the deepest descendant.
    self._subtree_depth = 0

    # The tree structure is locked and immutable. `stmt_depth` and
    # `subtree_depth` have been computed and stored.
    self._locked = False

    assert isinstance(pnode, parser.TreeNode)

  @property
  def name(self):
    # pylint: disable=protected-access
    return self.__class__.__name__

  @property
  def colextent(self):
    return self._colextent

  @property
  def reflow_valid(self):
    return self._reflow_valid

  @property
  def position(self):
    return Cursor(*self._position)

  # TODO(josh): rename this
  @property
  def type(self):
    return self.pnode.node_type

  # NOTE(josh): making children a property disallows direct assignment
  @property
  def children(self):
    return self._children

  @property
  def wrap(self):
    return self._wrap

  def __repr__(self):
    return "{},{}({}) p({},{}) ce:{}".format(
        self.type.name,
        self._wrap.name,
        self._passno,
        self.position[0], self.position[1],
        self.colextent)

  def has_terminal_comment(self):
    return False

  def get_depth(self):
    """
    Compute and return the depth of the subtree rooted at this node. The
    depth of the tree is the depth of the deepest (leaf) descendant.
    """

    if self._children:
      return 1 + max(child.get_depth() for child in self._children)
    return 1

  # Lock the tree structure and prevent further updates.
  # Compute `stmt_depth` and `subtree_depth`. Replace the children list with
  # a tuple.
  def lock(self, config, stmt_depth=0):
    self._stmt_depth = stmt_depth
    self._subtree_depth = self.get_depth()
    self._children = tuple(self._children)
    self._locked = True

    if self.type == NodeType.STATEMENT:
      nextdepth = 1
    elif stmt_depth > 0:
      nextdepth = stmt_depth + 1
    else:
      nextdepth = 0

    for child in self._children:
      child.lock(config, nextdepth)

  # TODO(josh): get rid of this
  def _get_wrap(self, config, passno):
    algoidx = clamp(passno, 0, len(config.algorithm_order))
    algoid = config.algorithm_order[algoidx]

    # No vpack if dangling parens
    if config.dangle_parens and algoid == WrapAlgo.VPACK.value:
      algoidx += 1
      algoid = config.algorithm_order[algoidx]
    return WrapAlgo.from_id(algoid)

  def _reflow(self, config, cursor, passno):
    raise NotImplementedError()

  def _reflow_new(self, config, cursor, passno):
    return self._reflow(config, cursor, passno)

  def reflow(self, config, cursor, passno=0):
    """
    (re-)compute the layout of this node under the assumption that it should
    be placed at the given `cursor` on the current `passno`. The wrap algorithm
    used is given by the node's statement depth and the current `passno`.
    """
    assert self._locked
    assert isinstance(self.pnode, parser.TreeNode)

    self._position = Cursor(*cursor)
    outcursor = None
    for repass in range(passno + 1):
      self._passno = repass
      self._wrap = self._get_wrap(config, repass)
      self._reflow_valid = True
      if USE_NEW_ALGORITHM:
        outcursor = self._reflow_new(config, Cursor(*cursor), repass)
      else:
        outcursor = self._reflow(config, Cursor(*cursor), repass)
      # TODO(josh): this is too conservative. We don't need every row to
      # reserve a character for the final parenthesis, we just need the final
      # row to reserve a character.
      if self._wrap == WrapAlgo.HPACK:
        linewidth = config.linewidth - 1
      else:
        linewidth = config.linewidth
      if self._reflow_valid and self._colextent <= linewidth:
        break
    assert outcursor is not None
    return outcursor

  def _write(self, config, ctx):
    for child in self._children:
      child.write(config, ctx)

  def write(self, config, ctx):
    self._write(config, ctx)

  @staticmethod
  def create(pnode):
    # pylint: disable=too-many-return-statements
    if pnode.node_type in SCALAR_TYPES:
      return ScalarNode(pnode)
    if pnode.node_type == NodeType.ONOFFSWITCH:
      return OnOffSwitchNode(pnode)
    if pnode.node_type == NodeType.STATEMENT:
      return StatementNode(pnode)
    if pnode.node_type == NodeType.KWARGGROUP:
      return KwargGroupNode(pnode)
    if pnode.node_type == NodeType.ARGGROUP:
      return ArgGroupNode(pnode)
    if pnode.node_type in (NodeType.PARGGROUP,
                           NodeType.FLAGGROUP):
      return PargGroupNode(pnode)
    if pnode.node_type == NodeType.PARENGROUP:
      return ParenGroupNode(pnode)
    if pnode.node_type == NodeType.BODY:
      return BodyNode(pnode)
    if pnode.node_type == NodeType.FLOW_CONTROL:
      return FlowControlNode(pnode)
    if pnode.node_type == NodeType.COMMENT:
      return CommentNode(pnode)
    if pnode.node_type == NodeType.WHITESPACE:
      return WhitespaceNode(pnode)
    if pnode.node_type in PAREN_TYPES:
      return ParenNode(pnode)

    raise RuntimeError("Unexpected node type")


class ParenNode(LayoutNode):
  """Holds parenthesis '(' or ')' for statements or boolean groups."""

  @property
  def name(self):
    return self.type.name

  def _reflow(self, config, cursor, passno):
    """There is only one possible layout for this node."""
    self._colextent = cursor[1] + 1
    return cursor + (0, 1)

  def _write(self, config, ctx):
    if self.type == NodeType.LPAREN:
      ctx.outfile.write_at(self.position, '(')
    elif self.type == NodeType.RPAREN:
      ctx.outfile.write_at(self.position, ')')
    else:
      raise ValueError("Unrecognized paren type")


class ScalarNode(LayoutNode):
  """
  Holdes scalar tokens such as statement names, parentheses, or keyword or
  positional arguments.
  """

  def has_terminal_comment(self):
    if not self.children:
      return False

    if not self.children[-1].pnode.children:
      return False

    # Note: bracket comments do not count as terminal comments
    return self.children[-1].pnode.children[0].type == TokenType.COMMENT

  def _reflow(self, config, cursor, passno):
    """
    Reflow is pretty trivial for a scalar node. We don't have any choices to
    make, there is only one possible rendering.
    """

    assert self.pnode.children
    token = self.pnode.children[0]
    assert isinstance(token, lexer.Token)

    # This might be a multiline string or a multiline bracket argument. In
    # that case we need to normalize line endings and flow each line
    lines = normalize_line_endings(token.spelling).split('\n')
    line = lines.pop(0)
    cursor[1] += len(line)
    self._colextent = cursor[1]

    while lines:
      cursor[0] += 1
      cursor[1] = 0
      line = lines.pop(0)
      cursor[1] += len(line)
      self._colextent = max(self._colextent, cursor[1])

    # Scalar nodes might have terminal comments associated with them. They show
    # up as children in the layout graph. This is the only possible child of
    # a scalar node.
    children = list(self.children)
    if children:
      child = children.pop(0)

      # We should not have more than one terminal comment associated with a
      # given scalar node
      assert not children

      # The only kind of children we store for a scalar node are argument
      # comments.
      assert child.type == NodeType.COMMENT

      # Reflow the comment after the scalar
      cursor = child.reflow(config, cursor + (0, 1), passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

      if child.pnode.children[0].type == TokenType.BRACKET_COMMENT:
        # If the argument comment is a bracket comment then we are done
        return cursor

      # If the argument commment is a line comment then we must invalidate
      # HPACK since there is no way we can render a single line.
      if self.wrap in (WrapAlgo.HPACK, WrapAlgo.HWRAP):
        # NOTE(josh): if we have a non-bracket comment child associated with
        # this argument, then we cannot hpack
        self._reflow_valid = False

    return cursor

  def _reflow_new(self, config, cursor, passno):
    """
    Reflow is pretty trivial for a scalar node. We don't have any choices to
    make, there is only one possible rendering.
    """

    assert self.pnode.children
    token = self.pnode.children[0]
    assert isinstance(token, lexer.Token)

    # This might be a multiline string or a multiline bracket argument. In
    # that case we need to normalize line endings and flow each line
    lines = normalize_line_endings(token.spelling).split('\n')
    line = lines.pop(0)
    cursor[1] += len(line)
    self._colextent = cursor[1]

    while lines:
      cursor[0] += 1
      cursor[1] = 0
      line = lines.pop(0)
      cursor[1] += len(line)
      self._colextent = max(self._colextent, cursor[1])

    # Scalar nodes might have terminal comments associated with them. They show
    # up as children in the layout graph. This is the only possible child of
    # a scalar node.
    children = list(self.children)
    if children:
      child = children.pop(0)

      # We should not have more than one terminal comment associated with a
      # given scalar node
      assert not children

      # The only kind of children we store for a scalar node are argument
      # comments.
      assert child.type == NodeType.COMMENT

      # Reflow the comment after the scalar
      cursor = child.reflow(config, cursor + (0, 1), passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

    # TODO(josh): should scalar nodes have a notion of acceptance?
    # self._reflow_valid = \
    #   default_accept_layout(
    #       config, [], False, False, start_cursor,
    #       Cursor(cursor[0], self._colextent))
    return cursor

  def _write(self, config, ctx):
    if not ctx.is_active():
      return

    assert self.pnode.children
    token = self.pnode.children[0]
    assert isinstance(token, lexer.Token)

    spelling = normalize_line_endings(token.spelling)
    if self.type == NodeType.FUNNAME:
      command_case = config.resolve_for_command(token.spelling, "command_case")
      if command_case in ("lower", "upper"):
        spelling = getattr(token.spelling, command_case)()
      elif command_case == "canonical":
        spelling = config.resolve_for_command(
            token.spelling, "spelling", token.spelling.lower())
      else:
        assert command_case == "unchanged", (
            "Unrecognized command case {}".format(command_case))
    elif (self.type in (NodeType.KEYWORD, NodeType.FLAG)
          and config.keyword_case in ("lower", "upper")):
      spelling = getattr(token.spelling, config.keyword_case)()

    ctx.outfile.write_at(self.position, spelling)
    children = list(self.children)
    if children:
      child = children.pop(0)
      assert child.type == NodeType.COMMENT
      child.write(config, ctx)

    assert not children


class OnOffSwitchNode(LayoutNode):
  """
  Holds a special-case line comment token such as ``# cmake-format: off`` or
  ``# cmake-format: on``
  """

  @property
  def name(self):
    return self.pnode.children[0].type.name

  def has_terminal_comment(self):
    return True

  def _reflow(self, config, cursor, passno):
    """
    There is only one possible flow as this is a single-token
    """
    assert self.pnode.children
    token = self.pnode.children[0]
    assert isinstance(token, lexer.Token)

    # Canonicalize the output. The input regex may be more generous than this
    # exact string.
    if token.type == TokenType.FORMAT_ON:
      spelling = "# cmake-format: on"
    elif token.type == TokenType.FORMAT_OFF:
      spelling = "# cmake-format: off"

    cursor = cursor + (0, len(spelling))
    self._colextent = cursor[1]
    return cursor

  def _write(self, config, ctx):
    assert self.pnode.children
    token = self.pnode.children[0]
    assert isinstance(token, lexer.Token)

    if token.type == TokenType.FORMAT_ON:
      spelling = "# cmake-format: on"
      if ctx.offswitch_location is None:
        logging.warning(
            "'#cmake-format: on' with no corresponding 'off' at %d:%d",
            token.begin.line, token.begin.col)
      else:
        ctx.infile.seek(ctx.offswitch_location.offset, 0)
        copy_size = token.begin.offset - ctx.offswitch_location.offset
        copy_bytes = ctx.infile.read(copy_size)
        copy_text = copy_bytes.decode('utf-8')
        ctx.outfile.write(copy_text)
        ctx.offswitch_location = None
        ctx.outfile.forge_cursor(self.position)
    elif token.type == TokenType.FORMAT_OFF:
      spelling = "# cmake-format: off"
      ctx.offswitch_location = token.end

    ctx.outfile.write_at(self.position, spelling)


# TODO(josh): add more than just the primary algorithm to the passes that we
# take. These four should be the first four passes, but we also want to
# add a pass where we move statement comment to the next line, or we dangle
# the paren. The statement comment pass may be something we want to do *foreach*
# of the other options, while the dangle paren is probably the last thing we
# want to do ever (i.e. if we're already wrapped as much as possible and the
# paren still wont fit).
class StatementNode(LayoutNode):

  # NOTE(josh): StatementNode is the only node that overrides reflow(), the
  # rest override just _reflow()
  # TODO(josh): at this point the difference in the override is pretty minimal
  # so we should probably figure out how to remove it.
  def reflow(self, config, cursor, _=0):  # pylint: disable=unused-argument
    assert self._locked
    assert isinstance(self.pnode, parser.TreeNode)

    self._position = Cursor(*cursor)
    outcursor = None

    for repass in range(0, WrapAlgo.COUNT.value):
      self._passno = repass
      self._wrap = self._get_wrap(config, repass)
      self._reflow_valid = True
      if USE_NEW_ALGORITHM:
        outcursor = self._reflow_new(config, Cursor(*cursor), repass)
      else:
        outcursor = self._reflow(config, Cursor(*cursor), repass)
      if self._reflow_valid and self.colextent <= config.linewidth:
        break
    assert outcursor is not None
    return outcursor

  def _reflow_horizontal(self, config, cursor, passno, children):
    assert children
    child = children.pop(0)
    assert child.type == NodeType.LPAREN
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    while children:
      prev = child
      child = children.pop(0)

      if (child.type == NodeType.COMMENT and
          child.pnode.children[0].type is TokenType.COMMENT
          and prev.type != NodeType.RPAREN):
        self._reflow_valid = False

      # TODO(josh): RESUME HERE -- the following is only valid for HPACK.
      # For HWRAP we need to try the cursor + '0', and if that fails then
      # try the column_corsor + '\n'.

      # The first node after an LPAREN and the RPAREN itself are not padded
      if not(prev.type == NodeType.LPAREN or child.type == NodeType.RPAREN):
        cursor[1] += len(' ')

      if (children and children[0].type == NodeType.RPAREN):
        child.statement_terminal = True

      cursor = child.reflow(config, cursor, passno)
      self._reflow_valid &= child.reflow_valid
      # NOTE(josh): we must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._colextent = max(self._colextent, child.colextent)
    return cursor

  def _reflow_vertical(self, config, cursor, passno, children, start_cursor):
    # pylint: disable=too-many-statements
    assert children
    child = children.pop(0)
    assert child.type == NodeType.LPAREN
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    if self._wrap == WrapAlgo.VPACK:
      column_cursor = cursor
    elif self._wrap in (WrapAlgo.KWNVPACK, WrapAlgo.PNVPACK):
      column_cursor = start_cursor + Cursor(1, config.tab_size)
    else:
      raise RuntimeError("Unexepected wrap algorithm")

    # NOTE(josh): this logic is common to both VPACK and NVPACK, the only
    # difference is the starting position of the column_cursor
    prev = None
    cursor = Cursor(*column_cursor)
    scalar_seq = analyze_scalar_sequence(children)

    while children:
      if children[0].type == NodeType.RPAREN:
        break

      if (prev is None) or (prev.type not in SCALAR_TYPES):
        scalar_seq = analyze_scalar_sequence(children)
      child = children.pop(0)

      # TODO(josh): remove scalar_squence code
      # If both the previous and current nodes are scalar nodes and the two
      # are not part of a particularly long (by a configurable margin) sequence
      # of scalar nodes, then advance the cursor horizontally by one space and
      # try to pack the next child on the same line as the current one
      if prev is None:
        cursor = child.reflow(config, cursor, passno)
      elif (prev.type in SCALAR_TYPES
            and child.type in SCALAR_TYPES
            and scalar_seq.length <= config.max_subargs_per_line
            and not scalar_seq.has_comment):
        cursor[1] += len(' ')

        # But if the cursor has overflowed the line width allocation, then
        # we cannot. Note that if this is the last argument in a statement,
        # then we will pack an RPAREN at it's end... so we should include the
        # size of that RPAREN when determining if we overflow.
        cursor = child.reflow(config, cursor, passno)
        realized_extent = child.colextent
        if children[0].type == NodeType.RPAREN:
          realized_extent += 1
        if realized_extent > config.linewidth:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)
      else:
        # Otherwise the node is not special and we vpack as usual
        column_cursor[0] += 1
        cursor = Cursor(*column_cursor)
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0]
      prev = child

    assert children
    child = children.pop(0)
    assert child.type == NodeType.RPAREN, \
        "Expected RPAREN but got {}".format(child.type)

    # NOTE(josh): dangle parens if it wont fit on the current line or
    # if the user has requested us to always do so
    if config.dangle_parens and cursor[0] > start_cursor[0]:
      column_cursor[0] += 1
      cursor = Cursor(column_cursor[0], start_cursor[1])
    elif (cursor[1] >= config.linewidth
          and self._wrap.value > WrapAlgo.VPACK.value):
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.type == NodeType.COMMENT:
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.has_terminal_comment():
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)

    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    # Trailing comment
    if children:
      cursor[1] += 1
      child = children.pop(0)
      assert child.type == NodeType.COMMENT, \
          "Expected COMMENT after RPAREN but got {}".format(child.type)
      assert not children
      savecursor = Cursor(*cursor)
      cursor = child.reflow(config, cursor, passno)

      if child.colextent > config.linewidth:
        cursor = child.reflow(config, (savecursor[0] + 1, start_cursor[1]),
                              passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

    return cursor

  @property
  def name(self):
    return self.children[0].pnode.children[0].spelling.lower()

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a statement which is nominally allocated `linewidth`
    columns for packing. `linewidth` is only considered for hpacking of
    consecutive scalar arguments
    """
    funname = self.children[0]
    assert funname.type == NodeType.FUNNAME

    token = funname.pnode.children[0]
    assert isinstance(token, lexer.Token)

    start_cursor = Cursor(*cursor)
    self._colextent = cursor[1]

    # Layout of the statement name is always the same, we just write it out
    # at the current cursor
    children = list(self.children)
    assert children
    child = children.pop(0)
    assert child.type == NodeType.FUNNAME
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    if need_paren_space(token.spelling, config):
      cursor[1] += 1

    if self._wrap in (WrapAlgo.HPACK, WrapAlgo.HWRAP):
      if token.spelling.lower() in config.always_wrap:
        self._reflow_valid = False
      return self._reflow_horizontal(config, cursor, passno, children)

    return self._reflow_vertical(config, cursor, passno, children, start_cursor)

  def _reflow_new(self, config, cursor, passno):
    """
    Compute the size of a statement which is nominally allocated `linewidth`
    columns for packing. `linewidth` is only considered for hpacking of
    consecutive scalar arguments
    """
    # pylint: disable=too-many-statements
    funname = self.children[0]
    assert funname.type == NodeType.FUNNAME
    token = funname.pnode.children[0]
    assert isinstance(token, lexer.Token)

    start_cursor = Cursor(*cursor)
    self._colextent = cursor[1]

    # Layout of the statement name is always the same, we just write it out
    # at the current cursor
    children = list(self.children)
    assert children
    child = children.pop(0)
    assert child.type == NodeType.FUNNAME
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    if need_paren_space(token.spelling, config):
      cursor[1] += 1

    assert children
    child = children.pop(0)
    assert child.type == NodeType.LPAREN
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    nest, vertical = get_nest_wrap(passno)
    if nest:
      column_cursor = start_cursor + (1, config.tab_size)
      cursor = Cursor(*column_cursor)
    else:
      column_cursor = Cursor(*cursor)

    # NOTE(josh): STATEMENTs should have at most one ARGGROUP child between
    # parentheses. This logic is redundant, but it is left so that we can
    # compare against other nodes and hopefully unify them.
    while children and children[0].type != NodeType.RPAREN:
      prev = child
      child = children.pop(0)

      if prev.type == NodeType.LPAREN:
        # This is the first child of the statement the cursor is already in the
        # right position, regardless of current nesting or wrapping
        pass
      elif (prev.type == NodeType.COMMENT
            or prev.has_terminal_comment()
            or vertical):
        cursor[1] = column_cursor[1]
        cursor[0] += 1
      else:
        cursor[1] += 1

      if (children and children[0].type == NodeType.RPAREN):
        child.statement_terminal = True

      cursor = child.reflow(config, cursor, passno)
      if not vertical:
        # If we are in horizontal wrapping mode, then we need to check if the
        # child has overflowed the column. If so, then we need to move to the
        # next line and try again
        realized_extent = child.colextent
        if children[0].type == NodeType.RPAREN:
          # If this is the last node before the parenthesis then we need to
          # account for one extra character (the closing parenthesis)
          realized_extent += 1
        if realized_extent > config.linewidth:
          # If the realized extent overflows the column limit then we need to
          # insert a newline and try again
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      # We must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0]

    assert children
    prev = child
    child = children.pop(0)
    assert child.type == NodeType.RPAREN, \
        "Expected RPAREN but got {}".format(child.type)

    # NOTE(josh): dangle parens if it wont fit on the current line or
    # if the user has requested us to always do so
    if config.dangle_parens and cursor[0] > start_cursor[0]:
      column_cursor[0] += 1
      cursor = Cursor(column_cursor[0], start_cursor[1])
    elif (cursor[1] >= config.linewidth
          and self._wrap.value > WrapAlgo.VPACK.value):
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.type == NodeType.COMMENT:
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.has_terminal_comment():
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)

    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    # Trailing comment
    if children:
      cursor[1] += 1
      child = children.pop(0)
      assert child.type == NodeType.COMMENT, \
          "Expected COMMENT after RPAREN but got {}".format(child.type)
      assert not children
      savecursor = Cursor(*cursor)
      cursor = child.reflow(config, cursor, passno)

      if child.colextent > config.linewidth:
        # If the statement trailing comment does not fit in the current column
        # just move it to the next line.
        # TODO(josh): actually, if the RPAREN is not already dangling then
        # we should dangle the paren and keep the comment trailing the statement
        cursor = child.reflow(config, (savecursor[0] + 1, start_cursor[1]),
                              passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

    self._reflow_valid = \
        default_accept_layout(
            config, [token.spelling], nest, vertical,
            start_cursor, Cursor(cursor[0], self._colextent))
    return cursor

  def _write(self, config, ctx):
    if not ctx.is_active():
      return
    super(StatementNode, self)._write(config, ctx)


class KwargGroupNode(LayoutNode):

  def has_terminal_comment(self):
    if self.children[-1].type is NodeType.COMMENT:
      return True
    return self.children[-1].has_terminal_comment()

  @property
  def name(self):
    self.children[0].pnode.chidren[0].spelling.upper()

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a keyword argument group which is nominally allocated
    `linewidth` columns for packing. `linewidth` is only considered for hpacking
    of consecutive scalar arguments
    """

    start_cursor = Cursor(*cursor)

    children = list(self.children)
    assert children
    child = children.pop(0)
    assert child.type == NodeType.KEYWORD
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    keyword = parser.get_normalized_kwarg(child.pnode.children[0])
    self._colextent = child.colextent

    # KWARG groups cannot be HWRAPPED. If they need to wrap, they must
    # do so vertically.
    if self._wrap == WrapAlgo.HWRAP:
      self._reflow_valid = False

    if self._wrap in (WrapAlgo.HPACK, WrapAlgo.HWRAP):
      if len(children) > config.max_subargs_per_line:
        self._reflow_valid = False

      while children:
        cursor[1] += len(' ')
        child = children.pop(0)

        if (child.type == NodeType.COMMENT and
            child.pnode.children[0].type is TokenType.COMMENT):
          self._reflow_valid = False

        cursor = child.reflow(config, cursor, passno)
        self._reflow_valid &= child.reflow_valid
        self._colextent = max(self._colextent, child.colextent)

      return cursor

    if self._wrap == WrapAlgo.VPACK:
      cursor[1] += len(' ')
      column_cursor = Cursor(*cursor)
    elif self._wrap in (WrapAlgo.KWNVPACK, WrapAlgo.PNVPACK):
      column_cursor = start_cursor + Cursor(1, config.tab_size)
    else:
      raise RuntimeError("Unexepected wrap algorithm")

    # NOTE(josh): this logic is common to both VPACK and NVPACK, the only
    # difference is the starting position of the column_cursor
    prev = None
    cursor = Cursor(*column_cursor)
    scalar_seq = analyze_scalar_sequence(children)

    while children:
      if (prev is None) or (prev.type not in SCALAR_TYPES):
        scalar_seq = analyze_scalar_sequence(children)
      child = children.pop(0)

      # If both the previous and current nodes are scalar nodes and the two
      # are not part of a particularly long (by a configurable margin) sequence
      # of scalar nodes, then advance the cursor horizontally by one space and
      # try to pack the next child on the same line as the current one
      if prev is None:
        cursor = child.reflow(config, cursor, passno)
        self._reflow_valid &= child.reflow_valid
      elif (prev.type in SCALAR_TYPES
            and child.type in SCALAR_TYPES
            and (scalar_seq.length <= config.max_subargs_per_line
                 or keyword == 'COMMAND'
                 or keyword.startswith('--'))
            and not scalar_seq.has_comment):
        cursor[1] += len(' ')

        # But if the cursor has overflowed the line width allocation, then
        # we cannot
        cursor = child.reflow(config, cursor, passno)
        if child.colextent > config.linewidth:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)
      # Otherwise we fall back to vpack
      else:
        column_cursor[0] += 1
        cursor = Cursor(*column_cursor)
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0]
      prev = child

    return cursor


def filename_node_key(layout_node):
  return layout_node.pnode.children[0].spelling


class PargGroupNode(LayoutNode):

  def has_terminal_comment(self):
    if not self.children:
      return False
    if self.children[-1].type is NodeType.COMMENT:
      return True
    return self.children[-1].has_terminal_comment()

  def lock(self, config, stmt_depth=0):
    if config.autosort and self.pnode.sortable:
      argument_nodes = []
      for child in self._children:
        if child.pnode.node_type is NodeType.ARGUMENT:
          argument_nodes.append(child)
      argument_nodes = sorted(argument_nodes, key=filename_node_key)
      nodemap = {
          id(node): idx + 1 for idx, node in enumerate(argument_nodes)
      }
      sortlist = []

      keyidx = 0
      posidx = 0
      for child in self._children:
        if id(child) in nodemap:
          keyidx = nodemap[id(child)]
          posidx = 0

        sortlist.append((keyidx, posidx, child))
        posidx += 1
      self._children = [child for _, _, child in sorted(sortlist)]

    super(PargGroupNode, self).lock(config, stmt_depth)

  def _reflow_hpack(self, config, cursor, passno):
    if len(self.children) > config.max_subargs_per_line:
      self._reflow_valid = False

    children = list(self.children)
    prev = None

    while children:
      if prev is not None:
        cursor[1] += len(' ')
      child = children.pop(0)

      if (child.type == NodeType.COMMENT and
          child.pnode.children[0].type is TokenType.COMMENT):
        self._reflow_valid = False

      cursor = child.reflow(config, cursor, passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      prev = child
    return cursor

  def _reflow_hwrap(self, config, cursor, passno):
    # TODO(josh): max_subargs_per_line doesn't invalidate hwrap
    if len(self.children) > config.max_subargs_per_line:
      self._reflow_valid = False

    column_cursor = Cursor(*cursor)
    children = list(self.children)
    prev = None
    while children:
      if prev is not None:
        cursor[1] += len(' ')
      child = children.pop(0)

      if (child.type == NodeType.COMMENT and
          child.pnode.children[0].type is TokenType.COMMENT):
        self._reflow_valid = False

      cursor = child.reflow(config, cursor, passno)
      linewidth = config.linewidth

      # Reserve an extra character if we are the positional group of a
      # statement and we are in wrap mode
      if self.statement_terminal and not children:
        linewidth -= 1

      if child.colextent > linewidth:
        column_cursor[0] += 1
        cursor = Cursor(*column_cursor)
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      prev = child

    return cursor

  def _reflow_vpack(self, config, cursor, passno):
    # NOTE(josh): this logic is common to both VPACK and NVPACK, the only
    # difference is the starting position of the column_cursor
    children = list(self.children)
    prev = None
    column_cursor = Cursor(*cursor)
    scalar_seq = analyze_scalar_sequence(children)

    while children:
      if (prev is None) or (prev.type not in SCALAR_TYPES):
        scalar_seq = analyze_scalar_sequence(children)
      child = children.pop(0)

      # If both the previous and current nodes are scalar nodes and the two
      # are not part of a particularly long (by a configurable margin) sequence
      # of scalar nodes, then advance the cursor horizontally by one space and
      # try to pack the next child on the same line as the current one
      if prev is None:
        cursor = child.reflow(config, cursor, passno)
      elif (prev.type in SCALAR_TYPES
            and child.type in SCALAR_TYPES
            and (scalar_seq.length <= config.max_subargs_per_line)
            and not scalar_seq.has_comment):
        cursor[1] += len(' ')

        # But if the cursor has overflowed the line width allocation, then
        # we cannot
        cursor = child.reflow(config, cursor, passno)
        if child.colextent > config.linewidth:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)
      # Otherwise we fall back to vpack
      else:
        column_cursor[0] += 1
        cursor = Cursor(*column_cursor)
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0]
      prev = child

    return cursor

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a positional argument group
    """
    self._colextent = cursor.y

    if self._wrap is WrapAlgo.HPACK:
      return self._reflow_hpack(config, cursor, passno)

    if self._wrap is WrapAlgo.HWRAP:
      return self._reflow_hwrap(config, cursor, passno)

    return self._reflow_vpack(config, cursor, passno)

  def _reflow_new(self, config, cursor, passno):
    """
    Compute the size of the group of all children
    """
    children = list(self.children)
    self._colextent = cursor.y

    prev = None
    child = None
    # PARG groups do not nest, they nest by their parents
    _, vertical = get_nest_wrap(passno)
    column_cursor = Cursor(*cursor)

    numgroups = 0
    while children:
      prev = child
      child = children.pop(0)

      if prev is None:
        # This is the first child of the arg group so the cursor is already
        # at the right location and theres nothing for us to update
        pass
      elif (prev.type == NodeType.COMMENT
            or prev.has_terminal_comment()
            or vertical):
        cursor[1] = column_cursor[1]
        cursor[0] += 1
      else:
        cursor[1] += 1

      if self.statement_terminal and not children:
        child.statement_terminal = True

      cursor = child.reflow(config, cursor, passno)
      if not vertical:
        # If we are in horizontal wrapping mode, then we need to check if the
        # child has overflowed the available column width. If so, then we need
        # to wrap to the next line and try again

        needs_wrap = False
        if self.statement_terminal:
          # If this is the last node before the parenthesis then we need to
          # account for one extra character (the closing parenthesis)
          if cursor[1] + 1 > config.linewidth:
            needs_wrap = True

        if child.colextent > config.linewidth:
          # If the realized extent overflows the column limit then we need to
          # insert a newline and try again
          needs_wrap = True

        if needs_wrap:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)

      # NOTE(josh): we must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

      if isinstance(child, (PargGroupNode, KwargGroupNode)):
        numgroups += 1

    # TODO(josh): Should this number 2 be a configuration parameter?
    if numgroups > 2:
      self._reflow_valid = False
    return cursor


class ArgGroupNode(LayoutNode):

  def has_terminal_comment(self):
    """
    An ArgGroup is a container for one or more PARGGROUP, FLAGGROUP, or
    KWARGGROUP subtrees. Any terminal comment will belong to one of
    it's children.
    """
    return self.children and (self.children[-1].type is NodeType.COMMENT or
                              self.children[-1].has_terminal_comment())

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of the group of all children
    """
    # TODO(josh): breakup this function
    # pylint: disable=too-many-statements

    children = list(self.children)
    self._colextent = cursor.y

    prev = None
    if self._wrap in (WrapAlgo.HPACK, WrapAlgo.HWRAP):
      while children:
        child = children.pop(0)

        if (child.type == NodeType.COMMENT and
            child.pnode.children[0].type is TokenType.COMMENT):
          self._reflow_valid = False

        if prev is not None:
          cursor[1] += len(' ')

        if self.statement_terminal and not children:
          child.statement_terminal = True

        cursor = child.reflow(config, cursor, passno)
        prev = child

        # NOTE(josh): we must keep updating the extent after each child because
        # the child might be an argument with a multiline string or a bracket
        # argument... in which case HPACK might actually wrap to a newline.
        self._reflow_valid &= child.reflow_valid
        self._colextent = max(self._colextent, child.colextent)
      return cursor

    column_cursor = cursor
    while children:
      child = children.pop(0)
      cursor = Cursor(*column_cursor)
      cursor = child.reflow(config, cursor, passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0] + 1
      prev = child
    return cursor

  def _reflow_new(self, config, cursor, passno):
    """
    Compute the size of the group of all children
    """
    children = list(self.children)
    self._colextent = cursor.y

    prev = None
    child = None
    # Argument groups cannot nest since they have no prefix, they are nested by
    # their parent
    _, vertical = get_nest_wrap(passno)

    column_cursor = Cursor(*cursor)

    numgroups = 0
    while children:
      prev = child
      child = children.pop(0)

      if prev is None:
        # This is the first child of the arg group so the cursor is already
        # at the right location and theres nothing for us to update
        pass
      elif (prev.type == NodeType.COMMENT
            or prev.has_terminal_comment()
            or vertical):
        cursor[1] = column_cursor[1]
        cursor[0] += 1
      else:
        cursor[1] += 1

      if self.statement_terminal and not children:
        child.statement_terminal = True

      cursor = child.reflow(config, cursor, passno)
      if not vertical:
        # If we are in horizontal wrapping mode, then we need to check if the
        # child has overflowed the available columnt width. If so, then we need
        # to wrap to the next line and try again

        needs_wrap = False
        if child.statement_terminal:
          # If this is the last node before the parenthesis then we need to
          # account for one extra character (the closing parenthesis)
          if cursor[1] + 1 > config.linewidth:
            needs_wrap = True

        if child.colextent > config.linewidth:
          # If the realized extent overflows the column limit then we need to
          # insert a newline and try again
          needs_wrap = True

        if needs_wrap:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)

      # NOTE(josh): we must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

      if isinstance(child, (PargGroupNode, KwargGroupNode)):
        numgroups += 1

    # TODO(josh): Should this number 2 be a configuration parameter?
    if numgroups > 2:
      self._reflow_valid = False
    return cursor

  def _write(self, config, ctx):
    if not ctx.is_active():
      return
    super(ArgGroupNode, self)._write(config, ctx)


class ParenGroupNode(LayoutNode):
  # TODO(josh): does ParenGroupNode also need to override reflow() to make
  # sure that the trailing paren has a column slot in HPACK mode? i.e. the
  # same as StatementNode.

  def has_terminal_comment(self):
    children = list(self.children)
    while children and children[0].type != NodeType.RPAREN:
      children.pop(0)

    if children:
      children.pop(0)

    return (children
            and children[-1].pnode.children[0].type == TokenType.COMMENT)

  def _reflow_hwrap(self, config, cursor, passno):
    """
    Logic is the same for HPACK and HWRAP
    """
    self._colextent = cursor[1]
    children = list(self.children)
    if not children:
      return cursor

    assert children
    child = children.pop(0)
    assert child.type == NodeType.LPAREN
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    while children:
      prev = child
      child = children.pop(0)

      if (child.type == NodeType.COMMENT and
          child.pnode.children[0].type is TokenType.COMMENT):
        self._reflow_valid = False

      # The first node after an LPAREN and the RPAREN itself are not padded
      if not(prev.type == NodeType.LPAREN or child.type == NodeType.RPAREN):
        cursor[1] += len(' ')

      cursor = child.reflow(config, cursor, passno)
      # NOTE(josh): we must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
    return cursor

  def _reflow_vertical(self, config, cursor, passno):
    # pylint: disable=too-many-statements
    start_cursor = Cursor(*cursor)
    self._colextent = cursor[1]

    children = list(self.children)
    if not children:
      return cursor

    assert children
    child = children.pop(0)
    assert child.type == NodeType.LPAREN
    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    if self._wrap in (WrapAlgo.VPACK, WrapAlgo.KWNVPACK):
      column_cursor = cursor
    elif self._wrap == WrapAlgo.PNVPACK:
      column_cursor = start_cursor + Cursor(1, config.tab_size)
    else:
      raise RuntimeError("Unexpected wrap algorithm")

    # NOTE(josh): this logic is common to both VPACK and NVPACK, the only
    # difference is the starting position of the column_cursor
    prev = None
    cursor = Cursor(*column_cursor)
    scalar_seq = analyze_scalar_sequence(children)

    while children:
      if children[0].type == NodeType.RPAREN:
        break

      if (prev is None) or (prev.type not in SCALAR_TYPES):
        scalar_seq = analyze_scalar_sequence(children)
      child = children.pop(0)

      # If both the previous and current nodes are scalar nodes and the two
      # are not part of a particularly long (by a configurable margin) sequence
      # of scalar nodes, then advance the cursor horizontally by one space and
      # try to pack the next child on the same line as the current one
      if prev is None:
        cursor = child.reflow(config, cursor, passno)
      elif (prev.type in SCALAR_TYPES
            and child.type in SCALAR_TYPES
            and scalar_seq.length <= config.max_subargs_per_line
            and not scalar_seq.has_comment):
        cursor[1] += len(' ')

        # But if the cursor has overflowed the line width allocation, then
        # we cannot
        cursor = child.reflow(config, cursor, passno)
        if child.colextent > config.linewidth:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)
      # Otherwise we fall back to vpack
      else:
        column_cursor[0] += 1
        cursor = Cursor(*column_cursor)
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0]
      prev = child

    assert children
    child = children.pop(0)
    assert child.type == NodeType.RPAREN, \
        "Expected RPAREN but got {}".format(child.type)

    # NOTE(josh); dangle parens if it wont fit on the current line or
    # if the user has requested us to always do so
    if config.dangle_parens and cursor[0] > start_cursor[0]:
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif (cursor[1] >= config.linewidth
          and self._wrap.value > WrapAlgo.VPACK.value):
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.type == NodeType.COMMENT:
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)
    elif prev.has_terminal_comment():
      column_cursor[0] += 1
      cursor = Cursor(*column_cursor)

    cursor = child.reflow(config, cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)

    # Trailing comment
    if children:
      cursor[1] += 1
      child = children.pop(0)
      assert child.type == NodeType.COMMENT, \
          "Expected COMMENT after RPAREN but got {}".format(child.type)
      assert not children
      cursor = child.reflow(config, cursor, passno)

      if child.colextent > config.linewidth:
        cursor[0] += 1
        cursor[1] = start_cursor[1]
        cursor = child.reflow(config, cursor, passno)

      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
    return cursor

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a parenthtetical argument group which is nominally
    allocated `linewidth` columns for packing. `linewidth` is only considered
    for hpacking of consecutive scalar arguments
    """
    if self._wrap in (WrapAlgo.HPACK, WrapAlgo.HWRAP):
      return self._reflow_hwrap(config, cursor, passno)

    return self._reflow_vertical(config, cursor, passno)

  def _reflow_new(self, config, cursor, passno):
    """
    Compute the size of the group of all children
    """
    children = list(self.children)
    self._colextent = cursor.y

    prev = None
    child = None
    # Argument groups cannot nest since they have no prefix, they are nested by
    # their parent
    _, vertical = get_nest_wrap(passno)
    column_cursor = Cursor(*cursor)

    numgroups = 0
    while children:
      prev = child
      child = children.pop(0)

      if prev is None:
        # This is the first child of the arg group so the cursor is already
        # at the right location and theres nothing for us to update
        pass
      elif (prev.type == NodeType.COMMENT
            or prev.has_terminal_comment()
            or vertical):
        cursor[1] = column_cursor[1]
        cursor[0] += 1
      else:
        cursor[1] += 1

      if self.statement_terminal and not children:
        child.statement_terminal = True

      cursor = child.reflow(config, cursor, passno)
      if not vertical:
        # If we are in horizontal wrapping mode, then we need to check if the
        # child has overflowed the available columnt width. If so, then we need
        # to wrap to the next line and try again

        needs_wrap = False
        if child.statement_terminal:
          # If this is the last node before the parenthesis then we need to
          # account for one extra character (the closing parenthesis)
          if cursor[1] + 1 > config.linewidth:
            needs_wrap = True

        if child.colextent > config.linewidth:
          # If the realized extent overflows the column limit then we need to
          # insert a newline and try again
          needs_wrap = True

        if needs_wrap:
          column_cursor[0] += 1
          cursor = Cursor(*column_cursor)
          cursor = child.reflow(config, cursor, passno)

      # NOTE(josh): we must keep updating the extent after each child because
      # the child might be an argument with a multiline string or a bracket
      # argument... in which case HPACK might actually wrap to a newline.
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)

      if isinstance(child, (PargGroupNode, KwargGroupNode)):
        numgroups += 1

    # TODO(josh): Should this number 2 be a configuration parameter?
    if numgroups > 2:
      self._reflow_valid = False
    return cursor

  def _write(self, config, ctx):
    if not ctx.is_active():
      return
    super(ParenGroupNode, self)._write(config, ctx)


class BodyNode(LayoutNode):

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a body block
    """
    column_cursor = cursor
    self._colextent = 0
    for child in self.children:
      cursor = child.reflow(config, column_cursor, passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0] + 1

    return cursor


class FlowControlNode(LayoutNode):

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a flowcontrol block
    """
    self._colextent = 0
    column_cursor = Cursor(*cursor)

    children = list(self.children)
    assert children
    child = children.pop(0)
    assert child.type == NodeType.STATEMENT
    cursor = child.reflow(config, column_cursor, passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)
    column_cursor[0] = cursor[0] + 1

    assert children
    child = children.pop(0)
    assert child.type == NodeType.BODY
    cursor = child.reflow(config, column_cursor + (0, config.tab_size), passno)
    self._reflow_valid &= child.reflow_valid
    self._colextent = max(self._colextent, child.colextent)
    column_cursor[0] = cursor[0] + 1

    while True:
      assert children
      child = children.pop(0)
      assert child.type == NodeType.STATEMENT
      cursor = child.reflow(config, column_cursor, passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0] + 1

      if not children:
        break
      child = children.pop(0)
      assert child.type == NodeType.BODY
      cursor = child.reflow(config, column_cursor +
                            (0, config.tab_size), passno)
      self._reflow_valid &= child.reflow_valid
      self._colextent = max(self._colextent, child.colextent)
      column_cursor[0] = cursor[0] + 1

    return cursor


class CommentNode(LayoutNode):

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a comment block
    """
    if (len(self.pnode.children) == 1
        and isinstance(self.pnode.children[0], lexer.Token)
        and self.pnode.children[0].type == TokenType.BRACKET_COMMENT):
      # TODO(josh): cache content and lines and re-use in _write
      content = normalize_line_endings(self.pnode.children[0].spelling)

      # TODO(josh): dedup with ScalarNode logic
      lines = content.split('\n')
      line = lines.pop(0)
      cursor[1] += len(line)
      self._colextent = cursor[1]

      while lines:
        cursor[0] += 1
        cursor[1] = 0
        line = lines.pop(0)
        cursor[1] += len(line)
        self._colextent = max(self._colextent, cursor[1])
      return cursor

    allocation = config.linewidth - cursor[1]
    lines = list(format_comment_lines(self.pnode, config, allocation))
    self._colextent = cursor[1] + max(len(line) for line in lines)

    increment = (len(lines) - 1, len(lines[-1]))
    return cursor + increment

  def _write(self, config, ctx):
    if not ctx.is_active():
      return

    if (len(self.pnode.children) == 1
        and isinstance(self.pnode.children[0], lexer.Token)
        and self.pnode.children[0].type == TokenType.BRACKET_COMMENT):
      content = normalize_line_endings(self.pnode.children[0].spelling)
      ctx.outfile.write_at(self.position, content)
    else:
      allocation = config.linewidth - self.position[1]
      lines = list(format_comment_lines(self.pnode, config, allocation))
      for idx, line in enumerate(lines):
        ctx.outfile.write_at(self.position + (idx, 0), line)


class WhitespaceNode(LayoutNode):

  def _reflow(self, config, cursor, passno):
    """
    Compute the size of a whitespace block
    """
    self._colextent = 0
    return cursor

  def _write(self, config, ctx):
    return


def get_scalar_sequence_len(box_children):
  length = 0
  for child in box_children:
    # Child is not a scalar type
    if child.type not in SCALAR_TYPES:
      return length
    length += 1
  return length


def get_scalar_sequence_has_comment(box_children):
  # TODO(josh): rename this function. It really just indicates whether or
  # not a scalar is allowed to be hpacked.

  for child in box_children:
    # Child is not a scalar type
    if child.type not in SCALAR_TYPES:
      return False

    if len(child.pnode.children) > 1:
      return True

  return False


class ScalarSeq(object):
  def __init__(self, length, has_comment):
    self.length = length
    self.has_comment = has_comment


def analyze_scalar_sequence(box_children):
  return ScalarSeq(get_scalar_sequence_len(box_children),
                   get_scalar_sequence_has_comment(box_children))


def create_box_tree(pnode):
  """
  Recursively construct a layout tree from the given parse tree
  """

  layout_root = LayoutNode.create(pnode)
  child_queue = list(pnode.children)

  found_primary_arggroup = False
  while child_queue:
    pchild = child_queue.pop(0)
    if not isinstance(pchild, parser.TreeNode):
      continue

    # NOTE(josh); the primary argument group gets formatted specially because
    # the parens belong to the statement, not the group.
    if (pnode.node_type == NodeType.STATEMENT
        and pchild.node_type == NodeType.ARGGROUP
        and not found_primary_arggroup):
      child_queue = list(pchild.children) + child_queue
      found_primary_arggroup = True
      continue

    if (pchild.node_type == NodeType.WHITESPACE
        and pchild.count_newlines() < 2):
      continue

    if pchild.node_type in MATCH_TYPES:
      layout_root.children.append(create_box_tree(pchild))
  return layout_root


def layout_tree(parsetree_root, config, linewidth=None):
  if linewidth is None:
    linewidth = config.line_width

  root_box = create_box_tree(parsetree_root)
  root_box.lock(config)
  root_box.reflow(config, (0, 0))

  return root_box


def dump_tree(nodes, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for idx, node in enumerate(nodes):
    outfile.write(indent)
    if idx + 1 == len(nodes):
      outfile.write('└─ ')
    else:
      outfile.write('├─ ')

    if sys.version_info[0] < 3:
      outfile.write(repr(node).decode('utf-8'))
    else:
      outfile.write(repr(node))
    outfile.write('\n')

    if not hasattr(node, 'children'):
      continue

    if idx + 1 == len(nodes):
      dump_tree(node.children, outfile, indent + '    ')
    else:
      dump_tree(node.children, outfile, indent + '│   ')


def dump_tree_upto(nodes, history, outfile=None, indent=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if outfile is None:
    outfile = sys.stdout

  for idx, node in enumerate(nodes):
    outfile.write(indent)
    if idx + 1 == len(nodes):
      outfile.write('└─ ')
    else:
      outfile.write('├─ ')

    if history[0] is node:
      # ANSI red
      outfile.write("\u001b[31m")
      if sys.version_info[0] < 3:
        outfile.write(repr(node).decode('utf-8'))
      else:
        outfile.write(repr(node))
      # ANSI reset
      outfile.write("\u001b[0m")
    else:
      if sys.version_info[0] < 3:
        outfile.write(repr(node).decode('utf-8'))
      else:
        outfile.write(repr(node))
    outfile.write('\n')

    if not hasattr(node, 'children'):
      continue

    subhistory = history[1:]
    if not subhistory:
      continue

    if idx + 1 == len(nodes):
      dump_tree_upto(node.children, subhistory, outfile, indent + '    ')
    else:
      dump_tree_upto(node.children, subhistory, outfile, indent + '│   ')


def tree_string(nodes, history=None):
  outfile = io.StringIO()
  if history:
    dump_tree_upto(nodes, history, outfile)
  else:
    dump_tree(nodes, outfile)
  return outfile.getvalue()


def dump_tree_for_test(nodes, outfile=None, indent=None, increment=None):
  """
  Print a tree of node objects for debugging purposes
  """

  if indent is None:
    indent = ''

  if increment is None:
    increment = '  '

  if outfile is None:
    outfile = sys.stdout

  for node in nodes:
    outfile.write(indent)
    outfile.write("({}, {}, {}, {}, {}, [".format(
        node.type, node.wrap,
        node.position[0], node.position[1], node.colextent))

    if hasattr(node, 'children') and node.children:
      outfile.write('\n')
      dump_tree_for_test(node.children, outfile, indent + increment, increment)
      outfile.write(indent)
    outfile.write("]),\n")


def test_string(nodes, indent=None, increment=None):
  if indent is None:
    indent = ' ' * 0
  if increment is None:
    increment = ' ' * 2

  outfile = io.StringIO()
  dump_tree_for_test(nodes, outfile, indent, increment)
  return outfile.getvalue()


class CursorFile(object):
  def __init__(self, config):
    self._fobj = io.StringIO()
    self._cursor = Cursor(0, 0)
    self._config = config

  @property
  def cursor(self):
    return Cursor(*self._cursor)

  def assert_at(self, cursor):
    assert (self._cursor[0] == cursor[0]
            and self._cursor[1] == cursor[1]), \
        "self._cursor=({},{}), write_at=({}, {}):\n{}".format(
            self._cursor[0], self._cursor[1], cursor[0], cursor[1],
            self.getvalue())

  def assert_lt(self, cursor):
    assert ((self._cursor[0] < cursor[0]) or (
        self._cursor[0] == cursor[0] and self._cursor[1] <= cursor[1])), \
        "self._cursor=({},{}), write_at=({}, {}):\n{}".format(
            self._cursor[0], self._cursor[1], cursor[0], cursor[1],
            self.getvalue().encode('utf-8', errors='replace'))

  def forge_cursor(self, cursor):
    self._cursor = cursor

  def write_at(self, cursor, text):
    if sys.version_info[0] < 3 and isinstance(text, str):
      text = text.decode('utf-8')
    self.assert_lt(cursor)

    rows = (cursor[0] - self._cursor[0])
    if rows:
      self._fobj.write(self._config.endl * rows)
      self._cursor[0] += rows
      self._cursor[1] = 0

    cols = (cursor[1] - self._cursor[1])
    if cols:
      self._fobj.write(' ' * cols)
      self._cursor[1] += cols

    lines = text.split('\n')
    line = lines.pop(0)
    self._fobj.write(line)
    self._cursor[1] += len(line)

    while lines:
      self._fobj.write(self._config.endl)
      self._cursor[0] += 1
      self._cursor[1] = 0
      line = lines.pop(0)
      self._fobj.write(line)
      self._cursor[1] += len(line)

  def write(self, copy_text):
    if sys.version_info[0] < 3 and isinstance(copy_text, str):
      copy_text = copy_text.decode('utf-8')
    self._fobj.write(copy_text)

    if '\n' not in copy_text:
      self._cursor[1] += len(copy_text)
    else:
      self._cursor[0] += copy_text.count('\n')
      self._cursor[1] = len(copy_text.split('\n')[-1])

  def getvalue(self):
    return self._fobj.getvalue() + self._config.endl


class Global(object):
  """
  Global state for the writing functions
  """

  def __init__(self, config, infile_content):
    # The offset within the sourcefile of the end of the offswitch token

    self.offswitch_location = None
    if sys.version_info[0] < 3:
      assert isinstance(infile_content, unicode)

    # NOTE(josh): must be BytesIO because we use byte-offsets for raw
    # transcription (i.e. between cmake-format: off and cmake-format: on)
    self.infile = io.BytesIO(bytearray(infile_content, 'utf-8'))
    self.outfile = CursorFile(config)

  def is_active(self):
    return self.offswitch_location is None


def write_tree(root_box, config, infile_content):
  """
  Format the tree for size only, then print all of the boxes to outfile
  """
  ctx = Global(config, infile_content)
  root_box.write(config, ctx)

  if not ctx.is_active():
    logging.warning("'# cmake-format: off' is never turned back 'on'"
                    "at %d:%d", ctx.offswitch_location.line,
                    ctx.offswitch_location.col)
  return ctx.outfile.getvalue()
