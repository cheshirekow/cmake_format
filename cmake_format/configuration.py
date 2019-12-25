from __future__ import unicode_literals

import logging

from cmake_format import commands
from cmake_format import markup
from cmake_format.config_util import (get_default, ConfigObject)


COMMENT_GROUP = (
    "bullet_char", "enum_char", "first_comment_is_literal",
    "literal_comment_pattern", "fence_pattern", "ruler_pattern",
    "hashruler_min_length", "canonicalize_hashrulers",
    "enable_markup")

MISC_GROUP = ("emit_byteorder_mark", "input_encoding", "output_encoding")


class LinterConfig(ConfigObject):   # pylint: disable=R0902
  """Options affecting the linter"""

  _extra_fields = [
      "disabled_codes",
      "function_pattern",
      "macro_pattern",
      "global_var_pattern",
      "internal_var_pattern",
      "local_var_pattern",
      "private_var_pattern",
      "public_var_pattern",
      "keyword_pattern",
      "max_conditionals_custom_parser",
      "min_statement_spacing",
      "max_statement_spacing",
      "max_returns",
      "max_branches",
      "max_arguments",
      "max_localvars",
      "max_statements"
  ]

  _vardocs = {
      "disabled_codes": (
          "a list of lint codes to disable"
      ),
      "function_pattern": (
          "regular expression pattern describing valid function names"
      ),
      "macro_pattern": (
          "regular expression pattern describing valid macro names"
      ),
      "global_var_pattern": (
          "regular expression pattern describing valid names for variables"
          " with global scope"
      ),
      "local_var_pattern": (
          "regular expression pattern describing valid names for variables"
          " with local scope"
      ),
      "keyword_pattern": (
          "regular expression pattern describing valid names for keywords"
          " used in functions or macros"
      ),
      "max_conditionals_custom_parser": (
          "In the heuristic for C0201, how many conditionals to match within"
          " a loop in before considering the loop a parser."
      ),
      "min_statement_spacing": (
          "Require at least this many newlines between statements"
      ),
      "max_statement_spacing": (
          "Require no more than this many newlines between statements"
      )
  }

  def __init__(self, **kwargs):
    self.disabled_codes = kwargs.pop(
        "disabled_codes", [])
    self.function_pattern = kwargs.pop(
        "function_pattern", "[0-9a-z_]+")
    self.macro_pattern = kwargs.pop(
        "macro_pattern", "[0-9A-Z_]+")
    self.global_var_pattern = kwargs.pop(
        "global_var_pattern", "[0-9A-Z][0-9A-Z_]+")
    self.internal_var_pattern = kwargs.pop(
        "internal_var_pattern", "_[0-9A-Z_]+")
    self.local_var_pattern = kwargs.pop(
        "local_var_pattern", "[0-9a-z][0-9a-z_]+")
    self.private_var_pattern = kwargs.pop(
        "private_var_pattern", "_[0-9a-z_]+")
    self.public_var_pattern = kwargs.pop(
        "public_var_pattern", "[0-9A-Z][0-9A-Z_]+")
    self.keyword_pattern = kwargs.pop(
        "keyword_pattern", "[0-9A-Z_]+")
    self.max_conditionals_custom_parser = kwargs.pop(
        "max_conditionals_custom_parser", 2)

    self.min_statement_spacing = kwargs.pop("min_statement_spacing", 1)
    self.max_statement_spacing = kwargs.pop("max_statement_spacing", 1)
    self.max_returns = kwargs.pop("max_returns", 6)
    self.max_branches = kwargs.pop("max_branches", 12)
    self.max_arguments = kwargs.pop("max_arguments", 5)
    self.max_localvars = kwargs.pop("max_localvars", 15)
    self.max_statements = kwargs.pop("max_statements", 50)


class Configuration(ConfigObject):
  """Various configuration options/parameters for formatting
  """
  # pylint: disable=too-many-arguments
  # pylint: disable=too-many-instance-attributes

  _extra_fields = [
      "linter",
  ]

  _group_map = [
      ("General Formatting Options", []),
      ("Options affecting comment formatting", COMMENT_GROUP),
      ("Miscellaneous options", MISC_GROUP),
  ]

  def __init__(
      self, line_width=80, tab_size=2,
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
      require_valid_layout=False,
      per_command=None,
      layout_passes=None,
      **kwargs):  # pylint: disable=W0613

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
    self.require_valid_layout = require_valid_layout

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

    self.linter = LinterConfig(**kwargs.pop("linter", {}))

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

Configuration._vardocs = VARDOCS = {  # pylint: disable=W0212
    "line_width": "How wide to allow formatted cmake files",
    "tab_size": "How many spaces to tab for indent",
    "max_subgroups_hwrap": (
        "If an argument group contains more than this many sub-groups "
        "(parg or kwarg groups), then force it to a vertical layout. "),
    "max_pargs_hwrap": (
        "If a positional argument group contains more than this many"
        " arguments, then force it to a vertical layout. "),
    "separate_ctrl_name_with_space": (
        "If true, separate flow control names from their parentheses with a"
        " space"),
    "separate_fn_name_with_space": (
        "If true, separate function names from parentheses with a space"),
    "dangle_parens": (
        "If a statement is wrapped to more than one line, than dangle the"
        " closing parenthesis on its own line."),
    "dangle_align": (
        "If the trailing parenthesis must be 'dangled' on its on line, then"
        " align it to this reference: `prefix`: the start of the statement, "
        " `prefix-indent`: the start of the statement, plus one indentation "
        " level, `child`: align to the column of the arguments"),
    "min_prefix_chars": (
        "If the statement spelling length (including space and parenthesis)"
        " is smaller than this amount, then force reject nested layouts."),
    "max_prefix_chars": (
        "If the statement spelling length (including space and parenthesis)"
        " is larger than the tab width by more than this amount, then"
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
        " remaining hash chars in a hash ruler, and normalize its length to"
        " fill the column"),
    "input_encoding": (
        "Specify the encoding of the input file. Defaults to utf-8."),
    "output_encoding": (
        "Specify the encoding of the output file. Defaults to utf-8. Note"
        " that cmake only claims to support utf-8 so be careful when using"
        " anything else"),
    "require_valid_layout": (
        "By default, if cmake-format cannot successfully fit everything into"
        " the desired linewidth it will apply the last, most agressive attempt"
        " that it made. If this flag is True, however, cmake-format will print"
        " error, exit with non-zero status code, and write-out nothing"),
    "per_command": (
        "A dictionary containing any per-command configuration overrides."
        " Currently only `command_case` is supported."),
    "layout_passes": (
        "A dictionary mapping layout nodes to a list of wrap decisions. See"
        " the documentation for more information."
    )
}
