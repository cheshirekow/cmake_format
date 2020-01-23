from __future__ import unicode_literals

import logging

from cmake_format import commands
from cmake_format import markup
from cmake_format.config_util import (
    FieldDescriptor, ConfigObject, SubtreeDescriptor)


class MarkupConfig(ConfigObject):
  """Options affecting comment reflow and formatting."""

  _field_registry = []

  bullet_char = FieldDescriptor(
      '*',
      "What character to use for bulleted lists"
  )

  enum_char = FieldDescriptor(
      '.',
      "What character to use as punctuation after numerals in an"
      " enumerated list"
  )
  first_comment_is_literal = FieldDescriptor(
      False,
      "If comment markup is enabled, don't reflow the first comment block"
      " in each listfile. Use this to preserve formatting of your"
      " copyright/license statements. "
  )
  literal_comment_pattern = FieldDescriptor(
      None,
      "If comment markup is enabled, don't reflow any comment block which"
      " matches this (regex) pattern. Default is `None` (disabled).",
  )
  fence_pattern = FieldDescriptor(
      markup.FENCE_PATTERN,
      "Regular expression to match preformat fences in comments"
      " default=r'{}'".format(markup.FENCE_PATTERN)
  )
  ruler_pattern = FieldDescriptor(
      markup.RULER_PATTERN,
      "Regular expression to match rulers in comments default=r'{}'"
      .format(markup.RULER_PATTERN)
  )
  explicit_trailing_pattern = FieldDescriptor(
      "#<",
      "If a comment line matches starts with this pattern then it is "
      "explicitly a trailing comment for the preceeding argument. Default "
      "is '#<'"
  )
  hashruler_min_length = FieldDescriptor(
      10,
      "If a comment line starts with at least this many consecutive hash "
      "characters, then don't lstrip() them off. This allows for lazy hash "
      "rulers where the first hash char is not separated by space"
  )
  canonicalize_hashrulers = FieldDescriptor(
      True,
      "If true, then insert a space between the first hash char and"
      " remaining hash chars in a hash ruler, and normalize its length to"
      " fill the column"
  )
  enable_markup = FieldDescriptor(
      True,
      "enable comment markup parsing and reflow"
  )

  def __init__(self, **kwargs):
    super(MarkupConfig, self).__init__(**kwargs)
    self.bullet_char = str(self.bullet_char)[0]
    self.enum_char = str(self.enum_char)[0]


class EncodingConfig(ConfigObject):
  """Options effecting file encoding"""

  _field_registry = []

  emit_byteorder_mark = FieldDescriptor(
      False,
      "If true, emit the unicode byte-order mark (BOM) at the start of"
      " the file"
  )
  input_encoding = FieldDescriptor(
      "utf-8",
      "Specify the encoding of the input file. Defaults to utf-8"
  )
  output_encoding = FieldDescriptor(
      "utf-8",
      "Specify the encoding of the output file. Defaults to utf-8. Note"
      " that cmake only claims to support utf-8 so be careful when using"
      " anything else"
  )


class LinterConfig(ConfigObject):
  """Options affecting the linter"""

  _field_registry = []

  disabled_codes = FieldDescriptor(
      [],
      "a list of lint codes to disable",
  )

  function_pattern = FieldDescriptor(
      "[0-9a-z_]+",
      "regular expression pattern describing valid function names"
  )

  macro_pattern = FieldDescriptor(
      "[0-9A-Z_]+",
      "regular expression pattern describing valid macro names"
  )

  global_var_pattern = FieldDescriptor(
      "[0-9A-Z][0-9A-Z_]+",
      "regular expression pattern describing valid names for variables"
      " with global scope"
  )

  internal_var_pattern = FieldDescriptor(
      "_[0-9A-Z][0-9A-Z_]+",
      "regular expression pattern describing valid names for variables"
      " with global scope (but internal semantic)"
  )

  local_var_pattern = FieldDescriptor(
      "[0-9a-z_]+",
      "regular expression pattern describing valid names for variables"
      " with local scope"
  )

  private_var_pattern = FieldDescriptor(
      "_[0-9a-z_]+",
      "regular expression pattern describing valid names for private"
      "directory variables"
  )

  public_var_pattern = FieldDescriptor(
      "[0-9A-Z][0-9A-Z_]+",
      "regular expression pattern describing valid names for public"
      "directory variables"
  )

  keyword_pattern = FieldDescriptor(
      "[0-9A-Z_]+",
      "regular expression pattern describing valid names for keywords"
      " used in functions or macros"
  )

  max_conditionals_custom_parser = FieldDescriptor(
      2,
      "In the heuristic for C0201, how many conditionals to match within"
      " a loop in before considering the loop a parser."
  )

  min_statement_spacing = FieldDescriptor(
      1,
      "Require at least this many newlines between statements"
  )

  max_statement_spacing = FieldDescriptor(
      1,
      "Require no more than this many newlines between statements"
  )

  max_returns = FieldDescriptor(6,)
  max_branches = FieldDescriptor(12,)
  max_arguments = FieldDescriptor(5,)
  max_localvars = FieldDescriptor(15,)
  max_statements = FieldDescriptor(50,)


ADDITIONAL_COMMANDS_DEMO = {
    'foo': {
        'flags': ['BAR', 'BAZ'],
        'kwargs': {
            'HEADERS': '*',
            'SOURCES': '*',
            'DEPENDS': '*'
        }
    }


}


class FormattingConfig(ConfigObject):
  """Options effecting formatting."""

  _field_registry = []

  line_width = FieldDescriptor(
      80,
      "How wide to allow formatted cmake files"
  )
  tab_size = FieldDescriptor(
      2,
      "How many spaces to tab for indent"
  )
  max_subgroups_hwrap = FieldDescriptor(
      2,
      "If an argument group contains more than this many sub-groups "
      "(parg or kwarg groups) then force it to a vertical layout. "
  )
  max_pargs_hwrap = FieldDescriptor(
      6,
      "If a positional argument group contains more than this many"
      " arguments, then force it to a vertical layout. "
  )
  max_rows_cmdline = FieldDescriptor(
      2,
      "If a cmdline positional group consumes more than this many lines"
      " without nesting, then invalidate the layout (and nest)"
  )
  separate_ctrl_name_with_space = FieldDescriptor(
      False,
      "If true, separate flow control names from their parentheses with a"
      " space"
  )
  separate_fn_name_with_space = FieldDescriptor(
      False,
      "If true, separate function names from parentheses with a space"
  )
  dangle_parens = FieldDescriptor(
      False,
      "If a statement is wrapped to more than one line, than dangle the"
      " closing parenthesis on its own line."
  )
  dangle_align = FieldDescriptor(
      "prefix",
      "If the trailing parenthesis must be 'dangled' on its on line, then"
      " align it to this reference: `prefix`: the start of the statement, "
      " `prefix-indent`: the start of the statement, plus one indentation "
      " level, `child`: align to the column of the arguments",
      ["prefix", "prefix-indent", "child", "off"],
  )
  min_prefix_chars = FieldDescriptor(
      4,
      "If the statement spelling length (including space and parenthesis)"
      " is smaller than this amount, then force reject nested layouts."
  )
  max_prefix_chars = FieldDescriptor(
      10,
      "If the statement spelling length (including space and parenthesis)"
      " is larger than the tab width by more than this amount, then"
      " force reject un-nested layouts."
  )
  max_lines_hwrap = FieldDescriptor(
      2,
      "If a candidate layout is wrapped horizontally but it exceeds this"
      " many lines, then reject the layout."
  )
  line_ending = FieldDescriptor(
      "unix",
      "What style line endings to use in the output.",
      ['windows', 'unix', 'auto']
  )
  command_case = FieldDescriptor(
      "canonical",
      "Format command names consistently as 'lower' or 'upper' case",
      ['lower', 'upper', 'canonical', 'unchanged']
  )
  keyword_case = FieldDescriptor(
      "unchanged",
      "Format keywords consistently as 'lower' or 'upper' case",
      ['lower', 'upper', 'unchanged']
  )
  always_wrap = FieldDescriptor(
      [],
      "A list of command names which should always be wrapped"
  )
  enable_sort = FieldDescriptor(
      True,
      "If true, the argument lists which are known to be sortable will be "
      "sorted lexicographicall"
  )
  autosort = FieldDescriptor(
      False,
      "If true, the parsers may infer whether or not an argument list is"
      " sortable (without annotation)."
  )
  require_valid_layout = FieldDescriptor(
      False,
      "By default, if cmake-format cannot successfully fit everything into"
      " the desired linewidth it will apply the last, most agressive"
      " attempt that it made. If this flag is True, however, cmake-format"
      " will print error, exit with non-zero status code, and write-out"
      " nothing"
  )

  layout_passes = FieldDescriptor(
      {},
      "A dictionary mapping layout nodes to a list of wrap decisions. See"
      " the documentation for more information."
  )

  def __init__(self, **kwargs):
    super(FormattingConfig, self).__init__(**kwargs)
    self.endl = None

  @property
  def linewidth(self):
    return self.line_width

  def set_line_ending(self, detected):
    self.endl = {
        "windows": "\r\n",
        "unix": "\n"
    }[detected]

  def _update_derived(self):
    """Update derived values after a potential config change
    """
    self.endl = {
        "windows": "\r\n",
        "unix": "\n",
        "auto": "\n"
    }[self.line_ending]


class ParseConfig(ConfigObject):
  """Options affecting listfile parsing"""

  _field_registry = []

  additional_commands = FieldDescriptor(
      ADDITIONAL_COMMANDS_DEMO,
      "Specify structure for custom cmake functions"
  )

  def _update_derived(self):
    if self.additional_commands is not None:
      for command_name, spec in self.additional_commands.items():
        self.fn_spec.add(command_name, **spec)

  def __init__(self, **kwargs):  # pylint: disable=W0613
    self.fn_spec = commands.get_fn_spec()
    super(ParseConfig, self).__init__(**kwargs)


class MiscConfig(ConfigObject):
  """Miscellaneous configurations options."""

  _field_registry = []

  per_command = FieldDescriptor(
      {},
      "A dictionary containing any per-command configuration overrides."
      " Currently only `command_case` is supported."
  )

  def __init__(self, **kwargs):  # pylint: disable=W0613
    per_command = kwargs.pop("per_command", {})
    super(MiscConfig, self).__init__(**kwargs)

    self.per_command = commands.get_default_config()
    for command, cdict in per_command.items():
      if not isinstance(cdict, dict):
        logging.warning("Invalid override of type %s for %s",
                        type(cdict), command)
        continue

      command = command.lower()
      if command not in self.per_command:
        self.per_command[command] = {}
      self.per_command[command].update(cdict)


class Configuration(ConfigObject):
  """Various configuration options/parameters for formatting
  """
  _field_registry = []

  parse = SubtreeDescriptor(ParseConfig)
  format = SubtreeDescriptor(FormattingConfig)
  markup = SubtreeDescriptor(MarkupConfig)
  lint = SubtreeDescriptor(LinterConfig)
  encode = SubtreeDescriptor(EncodingConfig)
  misc = SubtreeDescriptor(MiscConfig)

  def __init__(self, **kwargs):  # pylint: disable=W0613
    super(Configuration, self).__init__(**kwargs)

    # TODO(josh): this does not belong here! We need some global state for
    # formatting and the only thing we have accessible through the whole format
    # stack is this config object... so I'm abusing it by adding this field here
    self.first_token = None

  def resolve_for_command(self, command_name, config_key, default_value=None):
    """
    Check for a per-command value or override of the given configuration key
    and return it if it exists. Otherwise return the global configuration value
    for that key.
    """

    configpath = config_key.split(".")
    fieldname = configpath.pop(-1)
    configobj = self
    for subname in configpath:
      nextobj = getattr(configobj, subname, None)
      if nextobj is None:
        raise ValueError(
            "Config object {} does not have a subobject named {}"
            .format(type(configobj).__name__, subname))
      configobj = nextobj

    if hasattr(configobj, fieldname):
      assert default_value is None, (
          "Specifying a default value is not allowed if the config key exists "
          "in the global configuration ({})".format(config_key))
      default_value = getattr(configobj, fieldname)

    command_dict = self.misc.per_command.get(command_name.lower(), {})
    if config_key in command_dict:
      return command_dict[config_key]

    # legacy unqualified fieldname
    if fieldname in command_dict:
      return command_dict[fieldname]

    return default_value
