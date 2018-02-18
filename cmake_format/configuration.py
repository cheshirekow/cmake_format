import inspect
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
               separate_ctrl_name_with_space=False,
               separate_fn_name_with_space=False,
               bullet_char='*',
               enum_char=".",
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

    self.bullet_char = str(bullet_char)[0]
    self.enum_char = str(enum_char)[0]

    self.additional_commands = additional_commands

    self.fn_spec = commands.get_fn_spec()
    if additional_commands is not None:
      for command_name, spec in additional_commands.items():
        commands.decl_command(self.fn_spec, command_name, **spec)

  def clone(self):
    """
    Return a copy of self.
    """
    return Configuration(**self.as_dict())
