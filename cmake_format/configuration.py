import inspect
import logging
import sys

from cmake_format import commands


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
  elif string.lower() in ('n', 'no', 'f', 'false', '0', 'nope', 'nah', 'nada'):
    return False

  logging.warn("Ambiguous truthiness of string '%s' evalutes to 'FALSE'",
               string)
  return False


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


def get_default(value, default):
  """
  return ``value`` if it is not None, else default
  """
  if value is None:
    return default

  return value


class Configuration(ConfigObject):
  """
  Encapsulates various configuration options/parameters for formatting
  """

  # pylint: disable=too-many-arguments
  def __init__(self, line_width=80, tab_size=2,
               max_subargs_per_line=3,
               separate_ctrl_name_with_space=False,
               separate_fn_name_with_space=False,
               dangle_parens=False,
               bullet_char=None,
               enum_char=None,
               line_ending=None,
               additional_commands=None, **_):

    self.line_width = line_width
    self.tab_size = tab_size
    # TODO(josh): make this conditioned on certain commands / kwargs
    # because things like execute_process(COMMAND...) are less readable
    # formatted as a single list. In fact... special case COMMAND to break on
    # flags the way we do kwargs.
    self.max_subargs_per_line = max_subargs_per_line

    self.separate_ctrl_name_with_space = separate_ctrl_name_with_space
    self.separate_fn_name_with_space = separate_fn_name_with_space
    self.dangle_parens = dangle_parens

    self.bullet_char = str(bullet_char)[0]
    if bullet_char is None:
      self.bullet_char = u'*'

    self.enum_char = str(enum_char)[0]
    if enum_char is None:
      self.enum_char = u'.'

    self.line_ending = get_default(line_ending, u"unix")
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

    self.fn_spec = commands.get_fn_spec()
    if additional_commands is not None:
      for command_name, spec in additional_commands.items():
        commands.decl_command(self.fn_spec, command_name, **spec)

    assert self.line_ending in (u"windows", u"unix"), \
        r"Line ending must be either 'windows' or 'unix'"
    self.endl = {u'windows': u'\r\n',
                 u'unix': u'\n'}[self.line_ending]

  def clone(self):
    """
    Return a copy of self.
    """
    return Configuration(**self.as_dict())


VARCHOICES = {
    'line_ending': ['windows', 'unix']
}

VARDOCS = {
    "line_width": "How wide to allow formatted cmake files",
    "tab_size": "How many spaces to tab for indent",
    "max_subargs_per_line":
    "If arglists are longer than this, break them always",
    "separate_ctrl_name_with_space":
    "If true, separate flow control names from their parentheses with a"
    " space",
    "separate_fn_name_with_space":
    "If true, separate function names from parentheses with a space",
    "dangle_parens":
    "If a statement is wrapped to more than one line, than dangle the closing"
    " parenthesis on it's own line",
    "bullet_char":
    "What character to use for bulleted lists",
    "enum_char":
    "What character to use as punctuation after numerals in an enumerated"
    " list",
    "line_ending":
    "What style line endings to use in the output.",
    "additional_commands":
    "Specify structure for custom cmake functions"
}
