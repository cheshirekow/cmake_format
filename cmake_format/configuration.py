from __future__ import unicode_literals

import collections
import inspect
import io
import json
import logging
import pprint
import sys
import textwrap

from cmake_format import commands
from cmake_format import markup


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


def parse_bool(string):
  if string.lower() in ('y', 'yes', 't', 'true', '1', 'yup', 'yeah', 'yada'):
    return True
  if string.lower() in ('n', 'no', 'f', 'false', '0', 'nope', 'nah', 'nada'):
    return False

  logging.warning("Ambiguous truthiness of string '%s' evalutes to 'FALSE'",
                  string)
  return False


def get_default(value, default):
  """
  return ``value`` if it is not None, else default
  """
  if value is None:
    return default

  return value


COMMENT_GROUP = (
    "bullet_char", "enum_char", "first_comment_is_literal",
    "literal_comment_pattern", "fence_pattern", "ruler_pattern",
    "hashruler-min-length", "canonicalize_hashrulers",
    "enable_markup")

MISC_GROUP = ("emit_byteorder_mark", "input_encoding", "output_encoding")


def python_dump(cfg, outfile):
  ppr = pprint.PrettyPrinter(indent=2)
  format_buffer = io.StringIO()
  format_buffer.write("""
# --------------------------
# General Formatting Options
# --------------------------
""")
  comment_buffer = io.StringIO()
  comment_buffer.write("""
# --------------------------
# Comment Formatting Options
# --------------------------
""")
  misc_buffer = io.StringIO()
  misc_buffer.write("""
# ---------------------------------
# Miscellaneous Options
# ---------------------------------
""")
  for key in cfg.get_field_names():
    if key in COMMENT_GROUP:
      outbuf = comment_buffer
    elif key in MISC_GROUP:
      outbuf = misc_buffer
    else:
      outbuf = format_buffer

    helptext = VARDOCS.get(key, None)
    if helptext:
      for line in textwrap.wrap(helptext, 78):
        outbuf.write('# ' + line + '\n')
    value = getattr(cfg, key)
    if isinstance(value, dict):
      outbuf.write('{} = {}\n\n'.format(key, json.dumps(value, indent=2)))
    else:
      outbuf.write('{} = {}\n\n'.format(key, ppr.pformat(value)))
  outfile.write(format_buffer.getvalue())
  outfile.write(comment_buffer.getvalue())
  outfile.write(misc_buffer.getvalue())


class Configuration(object):
  """
  Encapsulates various configuration options/parameters for formatting
  """
  # pylint: disable=too-many-arguments
  # pylint: disable=too-many-instance-attributes

  @classmethod
  def get_field_names(cls):
    """
    Return a list of field names, extracted from kwargs to __init__().
    The order of fields in the tuple representation is the same as the order
    of the fields in the __init__ function
    """

    # NOTE(josh): args[0] is `self`
    if sys.version_info >= (3, 5, 0):
      sig = getattr(inspect, 'signature')(cls.__init__)
      return [field for field, _ in list(sig.parameters.items())[1:-1]]

    return getattr(inspect, 'getargspec')(cls.__init__).args[1:]

  def as_dict(self):
    """
    Return a dictionary mapping field names to their values only for fields
    specified in the constructor
    """
    return {field: serialize(getattr(self, field))
            for field in self.get_field_names()}

  def as_odict(self, with_comments=False):
    """
    Return a dictionary mapping field names to their values only for fields
    specified in the constructor
    """
    format_group = []
    comment_group = []
    misc_group = []

    for field in self.get_field_names():
      if field in COMMENT_GROUP:
        group = comment_group
      elif field in MISC_GROUP:
        group = misc_group
      else:
        group = format_group
      group.append((field, serialize(getattr(self, field))))

    out = collections.OrderedDict()
    if with_comments:
      out["_group0"] = ["General formatting options"]
    out.update(format_group)
    if with_comments:
      out["_group1"] = ["Options affecting comment formatting"]
    out.update(comment_group)
    if with_comments:
      out["_group2"] = ["Miscellaneous options"]
    out.update(misc_group)
    return out

  def __init__(self, line_width=80, tab_size=2,
               max_subgroups_hwrap=2,
               max_pargs_hwrap=6,
               separate_ctrl_name_with_space=False,
               separate_fn_name_with_space=False,
               dangle_parens=False,
               dangle_align=None,
               min_prefix_chars=4,
               max_prefix_chars=10,
               max_lines_hwrap=2,
               bullet_char=None,
               enum_char=None,
               line_ending=None,
               command_case=None,
               keyword_case=None,
               additional_commands=None,
               always_wrap=None,
               enable_sort=True,
               autosort=False,
               enable_markup=True,
               first_comment_is_literal=False,
               literal_comment_pattern=None,
               fence_pattern=None,
               ruler_pattern=None,
               emit_byteorder_mark=False,
               hashruler_min_length=10,
               canonicalize_hashrulers=True,
               input_encoding=None,
               output_encoding=None,
               per_command=None,
               layout_passes=None,
               **_):  # pylint: disable=W0613

    # pylint: disable=too-many-locals
    self.line_width = line_width
    self.tab_size = tab_size

    self.max_subgroups_hwrap = max_subgroups_hwrap
    self.max_pargs_hwrap = max_pargs_hwrap

    self.separate_ctrl_name_with_space = separate_ctrl_name_with_space
    self.separate_fn_name_with_space = separate_fn_name_with_space
    self.dangle_parens = dangle_parens
    self.dangle_align = get_default(dangle_align, "prefix")
    self.min_prefix_chars = min_prefix_chars
    self.max_prefix_chars = max_prefix_chars
    self.max_lines_hwrap = max_lines_hwrap

    self.bullet_char = str(bullet_char)[0]
    if bullet_char is None:
      self.bullet_char = '*'

    self.enum_char = str(enum_char)[0]
    if enum_char is None:
      self.enum_char = '.'

    self.line_ending = get_default(line_ending, "unix")
    self.command_case = get_default(command_case, "canonical")
    assert self.command_case in ("lower", "upper", "canonical", "unchanged")

    self.keyword_case = get_default(keyword_case, "unchanged")
    assert self.keyword_case in ("lower", "upper", "unchanged")

    self.additional_commands = get_default(additional_commands, {
        'foo': {
            'flags': ['BAR', 'BAZ'],
            'kwargs': {
                'HEADERS': '*',
                'SOURCES': '*',
                'DEPENDS': '*'
            }
        }
    })

    self.always_wrap = get_default(always_wrap, [])
    self.enable_sort = enable_sort
    self.autosort = autosort
    self.enable_markup = enable_markup
    self.first_comment_is_literal = first_comment_is_literal
    self.literal_comment_pattern = literal_comment_pattern
    self.fence_pattern = get_default(fence_pattern, markup.FENCE_PATTERN)
    self.ruler_pattern = get_default(ruler_pattern, markup.RULER_PATTERN)
    self.emit_byteorder_mark = emit_byteorder_mark
    self.hashruler_min_length = hashruler_min_length
    self.canonicalize_hashrulers = canonicalize_hashrulers

    self.layout_passes = get_default(layout_passes, {})

    self.input_encoding = get_default(input_encoding, "utf-8")
    self.output_encoding = get_default(output_encoding, "utf-8")

    self.fn_spec = commands.get_fn_spec()
    if additional_commands is not None:
      for command_name, spec in additional_commands.items():
        self.fn_spec.add(command_name, **spec)

    self.per_command = commands.get_default_config()
    for command, cdict in get_default(per_command, {}).items():
      if not isinstance(cdict, dict):
        logging.warning("Invalid override of type %s for %s",
                        type(cdict), command)
        continue

      command = command.lower()
      if command not in self.per_command:
        self.per_command[command] = {}
      self.per_command[command].update(cdict)

    assert self.line_ending in ("windows", "unix", "auto"), \
        r"Line ending must be either 'windows', 'unix', or 'auto'"
    self.endl = {'windows': '\r\n',
                 'unix': '\n',
                 'auto': '\n'}[self.line_ending]

    # TODO(josh): this does not belong here! We need some global state for
    # formatting and the only thing we have accessible through the whole format
    # stack is this config object... so I'm abusing it by adding this field here
    self.first_token = None

  def clone(self):
    """
    Return a copy of self.
    """
    return Configuration(**self.as_dict())

  def set_line_ending(self, detected):
    self.endl = {'windows': '\r\n',
                 'unix': '\n'}[detected]

  def resolve_for_command(self, command_name, config_key, default_value=None):
    """
    Check for a per-command value or override of the given configuration key
    and return it if it exists. Otherwise return the global configuration value
    for that key.
    """

    if hasattr(self, config_key):
      assert default_value is None, (
          "Specifying a default value is not allowed if the config key exists "
          "in the global configuration ({})".format(config_key))
      default_value = getattr(self, config_key)
    return (self.per_command.get(command_name.lower(), {})
            .get(config_key, default_value))

  @property
  def linewidth(self):
    return self.line_width


VARCHOICES = {
    "dangle_align": ["prefix", "prefix-indent", "child", "off"],
    'line_ending': ['windows', 'unix', 'auto'],
    'command_case': ['lower', 'upper', 'canonical', 'unchanged'],
    'keyword_case': ['lower', 'upper', 'unchanged'],
}

VARDOCS = {
    "line_width": "How wide to allow formatted cmake files",
    "tab_size": "How many spaces to tab for indent",
    "max_subgroups_hwrap": (
        "If an argument group contains more than this many sub-groups "
        "(parg or kwarg groups), then force it to a vertical layout. "),
    "max_pargs_hwrap": (
        "If a positinal argument group contains more than this many arguments, "
        "then force it to a vertical layout. "),
    "separate_ctrl_name_with_space": (
        "If true, separate flow control names from their parentheses with a"
        " space"),
    "separate_fn_name_with_space": (
        "If true, separate function names from parentheses with a space"),
    "dangle_parens": (
        "If a statement is wrapped to more than one line, than dangle the"
        " closing parenthesis on it's own line."),
    "dangle_align": (
        "If the trailing parenthesis must be 'dangled' on it's on line, then"
        " align it to this reference: `prefix`: the start of the statement, "
        " `prefix-indent`: the start of the statement, plus one indentation "
        " level, `child`: align to the column of the arguments"),
    "max_prefix_chars": (
        "If the statement spelling length (including space and parenthesis"
        " is larger than the tab width by more than this amoung, then"
        " force reject un-nested layouts."),
    "max_lines_hwrap": (
        "If a candidate layout is wrapped horizontally but it exceeds this"
        " many lines, then reject the layout."),
    "bullet_char": "What character to use for bulleted lists",
    "enum_char": (
        "What character to use as punctuation after numerals in an"
        " enumerated list"),
    "line_ending": "What style line endings to use in the output.",
    "command_case": (
        "Format command names consistently as 'lower' or 'upper' case"),
    "keyword_case": "Format keywords consistently as 'lower' or 'upper' case",
    "always_wrap": "A list of command names which should always be wrapped",
    "enable_sort": (
        "If true, the argument lists which are known to be sortable will be "
        "sorted lexicographicall"),
    "autosort": (
        "If true, the parsers may infer whether or not an argument list is"
        " sortable (without annotation)."),
    "enable_markup": "enable comment markup parsing and reflow",
    "first_comment_is_literal": (
        "If comment markup is enabled, don't reflow the first comment block"
        " in each listfile. Use this to preserve formatting of your"
        " copyright/license statements. "),
    "literal_comment_pattern": (
        "If comment markup is enabled, don't reflow any comment block which"
        " matches this (regex) pattern. Default is `None` (disabled)."),
    "fence_pattern": (
        "Regular expression to match preformat fences in comments"
        " default=r'{}'".format(markup.FENCE_PATTERN)),
    "ruler_pattern": (
        "Regular expression to match rulers in comments default=r'{}'"
        .format(markup.RULER_PATTERN)),
    "additional_commands": "Specify structure for custom cmake functions",
    "emit_byteorder_mark": (
        "If true, emit the unicode byte-order mark (BOM) at the start of"
        " the file"),
    "hashruler_min_length": (
        "If a comment line starts with at least this many consecutive hash "
        "characters, then don't lstrip() them off. This allows for lazy hash "
        "rulers where the first hash char is not separated by space"),
    "canonicalize_hashrulers": (
        "If true, then insert a space between the first hash char and"
        " remaining hash chars in a hash ruler, and normalize it's length to"
        " fill the column"),
    "input_encoding": (
        "Specify the encoding of the input file. Defaults to utf-8."),
    "output_encoding": (
        "Specify the encoding of the output file. Defaults to utf-8. Note"
        " that cmake only claims to support utf-8 so be careful when using"
        " anything else"),
    "per_command": (
        "A dictionary containing any per-command configuration overrides."
        " Currently only `command_case` is supported."),
    "layout_passes": (
        "A dictionary mapping layout nodes to a list of wrap decisions. See"
        " the documentation for more information."
    )
}
