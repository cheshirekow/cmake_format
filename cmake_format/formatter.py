import inspect
import re
import textwrap

from cmake_format import commands
from cmake_format import lexer
from cmake_format import parser

# Matches comment strings like ``# TODO(josh):`` or ``# NOTE(josh):``
NOTE_REGEX = re.compile(r'^[A-Z_]+\([^)]+\):.*')

# Matches comment lines that are clearly meant to separate sections or
# headers. The meaning of this regex is "a line consisting only of five or
# more non-word characters"
SEPARATOR_REGEX = re.compile(r'^\W{4}\W+$')


def serialize(obj):
  """
  Return a serializable representation of the object. If the object has an
  `as_dict` method, then it will call and return the output of that method.
  Otherwise return the object itself.
  """
  if hasattr(obj, 'as_dict'):
    fun = getattr(obj, 'as_dict')
    if callable(fun):
      return fun()

  return obj


class ConfigObject(object):
  """
  Provides simple serialization to a dictionary based on the assumption that
  all args in the __init__() function are fields of this object.
  """

  @classmethod
  def get_field_names(cls):
    """
    The order of fields in the tuple representation is the same as the order
    of the fields in the __init__ function
    """
    argspec = inspect.getargspec(cls.__init__)
    # NOTE(josh): args[0] is `self`
    return argspec.args[1:]

  def as_dict(self):
    """
    Return a dictionary mapping field names to their values only for fields
    specified in the constructor
    """
    return {field: serialize(getattr(self, field))
            for field in self.get_field_names()}


class Configuration(ConfigObject):
  """
  Encapsulates various configuration options/parameters for formatting
  """

  def __init__(self, line_width=80, tab_size=2,
               max_subargs_per_line=3,
               preserve_punctuation_lines=True,
               separate_ctrl_name_with_space=False,
               separate_fn_name_with_space=False,
               additional_commands=None, **_):
    self.line_width = line_width
    self.tab_size = tab_size
    # TODO(josh): make this conditioned on certain commands / kwargs
    # because things like execute_process(COMMAND...) are less readable
    # formatted as a single list. In fact... special case COMMAND to break on
    # flags the way we do kwargs.
    self.max_subargs_per_line = max_subargs_per_line
    self.preserve_punctuation_lines = preserve_punctuation_lines
    self.separate_ctrl_name_with_space = separate_ctrl_name_with_space
    self.separate_fn_name_with_space = separate_fn_name_with_space
    self.additional_commands = additional_commands

    self.fn_spec = commands.get_fn_spec()
    if additional_commands is not None:
      for command_name, spec in additional_commands.iteritems():
        commands.decl_command(self.fn_spec, command_name, **spec)

  def clone(self):
    """
    Return a copy of self.
    """
    return Configuration(**self.as_dict())


def indent_list(indent_str, lines):
  """
  Return a list of lines where indent_str is prepended to everything in lines.
  """
  return [indent_str + line for line in lines]


def stable_wrap(wrapper, paragraph_text):
  """
  textwrap doesn't appear to be stable. We run it multiple times until it
  converges
  """

  history = [paragraph_text]
  prev_text = paragraph_text
  for _ in range(8):
    lines = wrapper.wrap(prev_text)
    next_text = '\n'.join(line[2:] for line in lines)
    if next_text == prev_text:
      return lines
    prev_text = next_text
    history.append(next_text)

  assert False, ("textwrap failed to converge on:\n\n {}"
                 .format('\n\n'.join(history)))


def format_comment_block(config, line_width,  # pylint: disable=unused-argument
                         comment_lines):
  """
  Reflow a comment block into the given line_width. Return a list of lines.
  """
  stripped_lines = [line.strip().lstrip('#').strip()
                    for line in comment_lines]

  paragraph_lines = list()
  paragraphs = list()
  # A new "paragraph" starts at a paragraph boundary (double newline), or at
  # the start of a TODO(...): or NOTE(...):
  for line in stripped_lines:
    if NOTE_REGEX.match(line):
      if paragraph_lines:
        paragraphs.append(' '.join(paragraph_lines))
      paragraph_lines = [line]
    elif SEPARATOR_REGEX.match(line.strip()):
      if paragraph_lines:
        paragraphs.append(' '.join(paragraph_lines))
      paragraphs.append(line.rstrip())
      paragraph_lines = []
    elif line:
      paragraph_lines.append(line)
    else:
      if paragraph_lines:
        paragraphs.append('\n'.join(paragraph_lines))
      paragraphs.append('')
      paragraph_lines = []
  if paragraph_lines:
    paragraphs.append('\n'.join(paragraph_lines))

  lines = []
  for paragraph_text in paragraphs:
    if not paragraph_text:
      lines.append('#')
      continue
    wrapper = textwrap.TextWrapper(width=line_width,
                                   expand_tabs=True,
                                   replace_whitespace=True,
                                   drop_whitespace=True,
                                   initial_indent='# ',
                                   subsequent_indent='# ')

    lines.extend(stable_wrap(wrapper, paragraph_text))
  return lines


def is_flag(fn_spec, command_name, arg):
  """Return true if the given argument is a flag."""
  return fn_spec.get(command_name, {}).get(arg, 1) == 0


def is_kwarg(fn_spec, command_name, arg):
  """Return true if the given argument is a kwarg."""
  return fn_spec.get(command_name, {}).get(arg, 0) != 0


def split_args_by_kwargs(fn_spec, command_name, args):
  """
  Takes in a list of arguments and returns a list of lists. Each sublist
  is either a list of positional arguments, a list containg a kwarg
  followed by it's sub arguments, or a list containing a consecutive
  sequence of flags.
  """
  arg_split = [[]]
  for arg in args:
    if is_flag(fn_spec, command_name, arg.contents):
      if arg_split[-1]:
        if not is_flag(fn_spec, command_name, arg_split[-1][-1].contents):
          arg_split.append([])
    elif is_kwarg(fn_spec, command_name, arg.contents):
      if arg_split[-1]:
        arg_split.append([])
    arg_split[-1].append(arg)

  return arg_split


def arg_exists_with_comment(args):
  """Return true if any arg in the arglist contains a comment."""
  for arg in args:
    if arg.comments:
      return True
  return False


def format_single_arg(config,  # pylint: disable=unused-argument
                      line_width, arg):
  """
  Return a list of lines that reflow the single arg and all it's comments
  into a block with width at most line_width.
  """
  if arg.comments:
    comment_width = line_width - len(arg.contents) - 1
    if comment_width < 0:
      return None
    comment_lines = format_comment_block(config, comment_width, arg.comments)
    lines = [arg.contents + ' ' + comment_lines[0]]
    for comment_line in comment_lines[1:]:
      lines.append(' ' * (len(arg.contents) + 1) + comment_line)
    return lines

  return [arg.contents]


def split_shell_command(args):
  """
  Given a list of arguments to a COMMAND, try to match flags and split
  args into groups based on the location of flags (-f or --foo).
  """
  arglist = []
  for arg in args:
    if arg.contents.startswith('--'):
      arglist.append([arg])
    elif arglist:
      arglist[-1].append(arg)
    else:
      arglist.append([arg])
  return arglist


def format_shell_command(config, line_width, command_name, args):
  """Format arguments into a block with at most line_width chars."""

  # If there are no arguments with comments, then check to see how long the
  # line would be if we just catted the arguments together into a single line.
  # If that line is small enough to fit then we are done, and just return that
  # single line.
  if not arg_exists_with_comment(args):
    single_line = ' '.join([arg.contents for arg in args])
    if len(single_line) < line_width:
      return [single_line]

  lines = []
  arg_multilist = split_shell_command(args)

  # If there are multiple single flags (i.e. --foo --bar --baz) in a row
  # that do not have arguments, then we can join them together into a single
  # row that we try to format as one
  arg_multilist_filtered = []
  for arg_sublist in arg_multilist:
    if len(arg_sublist) == 1 and arg_multilist_filtered:
      arg_multilist_filtered[-1].append(arg_sublist[0])
    else:
      arg_multilist_filtered.append(arg_sublist)

  for arg_sublist in arg_multilist_filtered:
    sublist_lines = format_arglist(config, line_width, command_name,
                                   arg_sublist)
    lines.extend(sublist_lines)

  return lines


def join_parens(args):
  """
  Join parenthesis with whatever argument string they are nearest.
  """

  out = []
  cache = ""
  for arg in args:
    if arg == '(':
      cache += arg
    elif arg == ')':
      out[-1] += arg
    else:
      out.append(cache + arg)
      cache = ""
  return out


def format_kwarglist(config, line_width, command_name, args):
  """
  Given a list of arguments containing a KWARG in position [0], format into
  a list of lines.
  """
  kwarg = args[0].contents

  if len(args) == 1:
    return [kwarg]

  # If the KWARG is 'COMMAND' then let's not put one entry per line,
  # but fit as many command args per line as possible.
  if kwarg == 'COMMAND':
    # Copy the config and override max subargs per line
    config = config.clone()
    # pylint: disable=attribute-defined-outside-init
    config.max_subargs_per_line = 1e6

    aligned_indent_str = ' ' * (len(kwarg) + 1)
    tabbed_indent_str = ' ' * config.tab_size

    # Lines to append if we put them aligned with the end of the kwarg
    line_width_aligned = line_width - len(aligned_indent_str)
    lines_aligned = format_shell_command(config, line_width_aligned,
                                         args[1].contents, args[1:])

    # Lines to append if we put them on lines after the kwarg and
    # indented one block higher
    line_width_tabbed = line_width - len(tabbed_indent_str)
    lines_tabbed = format_shell_command(config, line_width_tabbed,
                                        args[1].contents, args[1:])

  else:
    aligned_indent_str = ' ' * (len(kwarg) + 1)
    tabbed_indent_str = ' ' * config.tab_size

    # Lines to append if we put them aligned with the end of the kwarg
    line_width_aligned = line_width - len(aligned_indent_str)
    lines_aligned = format_arglist(config, line_width_aligned,
                                   command_name, args[1:])

    # Lines to append if we put them on lines after the kwarg and
    # indented one block higher
    line_width_tabbed = line_width - len(tabbed_indent_str)
    lines_tabbed = format_arglist(config, line_width_tabbed,
                                  command_name, args[1:])

  # If aligned doesn't fit, then use tabbed
  if get_block_width(lines_aligned) > line_width - len(aligned_indent_str):
    return [kwarg] + indent_list(tabbed_indent_str, lines_tabbed)

  return ([kwarg + ' ' + lines_aligned[0]]
          + indent_list(aligned_indent_str, lines_aligned[1:]))


def format_nonkwarglist(config, line_width, args):
  """
  Given a list arguments containing no KWARGS, format into a list of lines
  """
  indent_str = ''
  lines = ['']

  # TODO(josh): if aligning after the KWARG exeeds line width, then move one
  # line below and align to the start + one indent.

  # if the there are "lots" of arguments in the list, put one per line,
  # but we can't reuse the logic below since we do want to append to the
  # first line.
  if len(args) > config.max_subargs_per_line:
    first_lines = format_single_arg(config, line_width - len(indent_str),
                                    args[0])
    if lines[-1]:
      lines[-1] += ' '
    lines[-1] += first_lines[0]
    for line in first_lines[1:]:
      lines.append(indent_str + line)
    for arg in args[1:]:
      for line in format_single_arg(config,
                                    line_width - len(indent_str), arg):
        lines.append(indent_str + line)
    return lines

  for arg in args:
    # Lines to add if we were to put the arg at the end of the current line.
    if lines[-1]:
      arg_linelen = line_width - len(lines[-1]) - 1
    else:
      arg_linelen = line_width - len(lines[-1])

    if arg_linelen >= len(arg.contents):
      lines_append = format_single_arg(config, arg_linelen, arg)
    else:
      lines_append = None

    # Lines to add if we are going to make a new line for this arg
    lines_new = format_single_arg(
        config, line_width - len(indent_str), arg)

    # If going to a new line greatly reduces the number of lines required
    # then choose that option over the latter.
    if (lines_append is None
            # pylint: disable=bad-continuation
            or len(lines_append[0]) + len(lines[-1]) + 1 > line_width
            or 4 * len(lines_new) < len(lines_append)):
      for line in lines_new:
        lines.append(indent_str + line)
    else:
      arg_indent_str = ' ' * (len(lines[-1]) + 1)
      if lines[-1]:
        lines[-1] += ' '
      lines[-1] += lines_append[0]

      for line in lines_append[1:]:
        lines.append(arg_indent_str + line)

  return lines


def format_arglist(config, line_width, command_name, args):
  """
  Given a list arguments containing at most one KWARG (in position [0]
  if it exists), format into a list of lines.
  """
  if len(args) < 1:
    return []

  if is_kwarg(config.fn_spec, command_name, args[0].contents):
    return format_kwarglist(config, line_width, command_name, args)

  return format_nonkwarglist(config, line_width, args)


def format_args(config, line_width, command_name, args):
  """Format arguments into a block with at most line_width chars."""

  # If there are no arguments that contain a comment, then attempt to
  # pack all of the arguments onto a single line
  if not arg_exists_with_comment(args):
    single_line = ' '.join(join_parens([arg.contents for arg in args]))
    if len(single_line) < line_width:
      return [single_line]

  lines = []
  arg_multilist = split_args_by_kwargs(config.fn_spec, command_name, args)

  # Look for strings of single arguments that can be joined together
  arg_multilist_filtered = []
  for arg_sublist in arg_multilist:

    max_subargs = config.max_subargs_per_line
    if len(arg_sublist) == 1 and arg_multilist_filtered \
            and len(arg_multilist_filtered[-1]) < max_subargs:
      arg_multilist_filtered[-1].append(arg_sublist[0])
    else:
      arg_multilist_filtered.append(arg_sublist)

  for arg_sublist in arg_multilist_filtered:
    sublist_lines = format_arglist(config, line_width, command_name,
                                   arg_sublist)
    lines.extend(sublist_lines)

  return lines


def get_block_width(lines):
  """Return the max width of any line within the list of lines."""
  return max(len(line) for line in lines)


def is_control_statement(command_name):
  return command_name.lower() in [
      'if', 'elseif', 'else', 'endif',
      'while', 'endwhile',
      'foreach', 'endforeach',
      'function', 'endfunction',
      'macro', 'endmacro',
      'continue', 'break', 'return',
  ]


def format_command(config, command, line_width):
  """
  Formats a cmake command call into a block with at most line_width chars.
  Returns a list of lines.
  """

  if (config.separate_fn_name_with_space or
      # pylint: disable=bad-continuation
      (is_control_statement(command.name)
          and config.separate_ctrl_name_with_space)):
    command_start = command.name + ' ('
  else:
    command_start = command.name + '('

  # If there are no args then return just the command
  if len(command.body) < 1:
    return [command_start + ')']
  else:
    # Format args into a block that is aligned with the end of the
    # parenthesis after the command name
    lines_a = format_args(config, line_width - len(command_start),
                          command.name, command.body)

    # Format args into a block that is aligned with the command start
    # plus one tab size
    lines_b = format_args(config,
                          line_width - config.tab_size,
                          command.name, command.body)

    # If the version aligned with the comand start + indent has *alot*
    # fewer lines than the version aligned with the command end, then
    # use this one. Also use it if the first option exceeds line width.
    if len(lines_a) > 4 * len(lines_b) \
            or get_block_width(lines_a) > line_width - len(command_start):
      lines = [command_start]
      indent_str = ' ' * config.tab_size
      for line in lines_b:
        lines.append(indent_str + line)
      if len(lines[-1]) < line_width and not command.body[-1].comments:
        lines[-1] += ')'
      else:
        lines.append(indent_str[:-1] + ')')

    # Otherwise use the version that is aligned with the command ending
    else:
      lines = [command_start + lines_a[0]]
      indent_str = ' ' * len(command_start)
      for line in lines_a[1:]:
        lines.append(indent_str + line)
      if len(lines[-1]) < line_width and not command.body[-1].comments:
        lines[-1] += ')'
      else:
        lines.append(indent_str[:-1] + ')')

    # If the command itself has a trailing line comment then attempt to
    # keep the comment attached to the command, but consider also moving
    # the comment to it's own line if that uses up a lot less lines.
    if command.comment:
      line_width_append = line_width - len(lines[-1]) - 1
      comment_lines_append = format_comment_block(config,
                                                  line_width_append,
                                                  [command.comment])

      comment_lines_extend = format_comment_block(config, line_width,
                                                  [command.comment])

      if len(comment_lines_append) < 4 * len(comment_lines_extend):
        append_indent = ' ' * (len(lines[-1]) + 1)
        lines[-1] += ' ' + comment_lines_append[0]
        lines.extend(indent_list(append_indent,
                                 comment_lines_append[1:]))
      else:
        lines.extend(comment_lines_extend)
  return lines


def write_indented(outfile, indent_str, lines):
  """Write lines to outfile prefixed with indent_str."""

  for line in lines:
    outfile.write(indent_str)
    outfile.write(line)
    outfile.write('\n')


class TreePrinter(object):
  """
  Maintains printing state and implements node printers for various types of
  nodes in the full-syntax-tree.
  """

  def __init__(self, config, outfile):
    self.config = config
    self.outfile = outfile
    self.scope_depth = 0
    self.active = True

  def get_indent_size(self):
    """
    Return the current size of an indent composed of ``depth`` tabs.
    """
    return self.config.tab_size * self.scope_depth

  def get_indent(self):
    """
    Return an indentation string appropriate for the current scope depth.
    """
    return ' ' * self.get_indent_size()

  def get_line_width(self):
    """
    Return the current line width that we should be trying to format listfiles
    to, found by configuration minus indentation.
    """
    return self.config.line_width - self.get_indent_size()

  def print_block(self, node):
    """
    Print a block node. Block nodes don't have content, so we just recurse and
    print all children.
    """
    for child in node.children:
      self.print_node(child)

  def print_comment_tokens(self, tokens):
    """
    Print comment tokens. If the formatter is currently inactive, then just
    iterate over tokens in serial order and print them out the same way they
    were in the input file. If the formatter is active, then reflow and
    hard-wrap the comment text and print out the resulting lines.
    """

    if self.active:
      # Strip newline tokens and remove the comment char
      lines = [token.content[1:] for token in tokens
               if token.type in parser.COMMENT_TOKENS]
      lines = format_comment_block(self.config, self.get_line_width(),
                                   lines)

      # NOTE(josh): since we callback inside print_comment() if we see an
      # on/off sentinel it's possible that we actually have no lines cached
      # and so no lines to print.
      if not lines:
        return

      for line in lines[:-1]:
        self.outfile.write(self.get_indent())
        self.outfile.write(line.rstrip())
        self.outfile.write('\n')
      self.outfile.write(self.get_indent())
      self.outfile.write(lines[-1].rstrip())
    else:
      for token in tokens:
        self.outfile.write(token.content)

  def print_comment(self, node):
    """
    Print a comment node. A comment node is composed of a continuous sequence
    of comment lines. Nominally we will reflow the comment text but we also
    watch for sentinel tokens that activate/deactivate the formatter.
    """

    # If the formatter is active, we'll collect up comment tokens into this
    # cache so we can pass them all to the formatter which will reflow and
    # word-wrap them.
    cache = []
    tokens = list(node.content.tokens)
    while tokens:
      token = tokens.pop(0)
      if token.type == lexer.FORMAT_OFF:
        self.print_comment_tokens(cache)
        if cache:
          self.outfile.write('\n')
        cache = [token]
        self.active = False
      elif token.type == lexer.FORMAT_ON:
        cache.append(token)
        if tokens and tokens[0].type == lexer.NEWLINE:
          cache.append(tokens.pop(0))
        self.print_comment_tokens(cache)
        self.active = True
        cache = []
      else:
        if self.active:
          if token.type == lexer.COMMENT:
            cache.append(token)
        else:
          cache.append(token)

    self.print_comment_tokens(cache)

  def print_whitespace(self, node):
    """
    Print a whitespace node. A whitespace node is composed of a continuous
    sequence of whitespace tokens between either comment or cmake nodes. If
    the formatter is active we will collapse whitespace into 0, 1, or 2
    newlines. Otehrwise we will print all tokens as they were in the infile.
    """
    if self.active:
      # Block-level whitespace is collapsed into exactly one or two newlines
      if node.count_newlines() > 1:
        self.outfile.write('\n\n')
      else:
        self.outfile.write('\n')
    else:
      for token in node.content.tokens:
        self.outfile.write(token.content)

  def print_statement(self, node):
    """
    Print a cmake statement. The format function will return a list of formatted
    lines so if the formatter is active we just print those lines out with an
    appropriate indentation. If the formatter is inactive we just print out
    all the tokens in the same way they were in the infile.
    """

    if self.active:
      lines = format_command(self.config, node, self.get_line_width())
      for line in lines[:-1]:
        self.outfile.write(self.get_indent())
        self.outfile.write(line.rstrip())
        self.outfile.write('\n')
      self.outfile.write(self.get_indent())
      self.outfile.write(lines[-1].rstrip())
    else:
      for token in node.prefix_tokens:
        self.outfile.write(token.content)
      for arg in node.body:
        for token in arg.tokens:
          self.outfile.write(token.content)
      for token in node.postfix_tokens:
        self.outfile.write(token.content)

    self.scope_depth += 1
    self.print_block(node)
    self.scope_depth -= 1

  def print_node(self, node):
    """
    Print dispatch: will call the correct print function depending on the type
    of node.
    """
    if node.node_type == parser.BLOCK_NODE:
      self.print_block(node)
    elif node.node_type == parser.COMMENT_NODE:
      self.print_comment(node)
    elif node.node_type == parser.WHITESPACE_NODE:
      self.print_whitespace(node)
    elif node.node_type == parser.STATEMENT_NODE:
      self.print_statement(node)
    else:
      assert False, ("Unrecognized node type: {} ({})"
                     .format(parser.kNodeTypeToStr(node.node_type),
                             node.node_type))
