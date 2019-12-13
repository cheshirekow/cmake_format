import collections
import contextlib
import inspect
import logging
import pprint
import sys
import textwrap

logger = logging.getLogger(__name__)

def serialize(obj):
  """
  Return a serializable representation of the object. If the object has an
  `as_dict` method, then it will call and return the output of that method.
  Otherwise return the object itself.
  """
  if hasattr(obj, 'as_odict'):
    fun = getattr(obj, 'as_odict')
    if callable(fun):
      return fun()
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

  logger.warning("Ambiguous truthiness of string '%s' evalutes to 'FALSE'",
                 string)
  return False


def get_default(value, default):
  """
  return ``value`` if it is not None, else default
  """
  if value is None:
    return default

  return value


class ExecGlobal(dict):
  """
  We pass this in as the "global" variable when parsing a config. It is
  composed of a nested dictionary and provides methods for mangaging
  the current  "stack" into that nested dictionary
  """

  def __init__(self, filepath):
    super(ExecGlobal, self).__init__()

    # The current stack of push/pop config sections
    self._dict_stack = []

    # This is what we provide for __file__
    self.filepath = filepath

  @contextlib.contextmanager
  def section(self, key):
    self.push_section(key)
    yield None
    self.pop_section()

  def push_section(self, key):
    key = key.replace("-", "_")
    if self._dict_stack:
      stacktop = self._dict_stack[-1]
    else:
      stacktop = self

    if key not in stacktop:
      stacktop[key] = {}
    newtop = stacktop[key]
    self._dict_stack.append(newtop)

  def pop_section(self):
    self._dict_stack.pop(-1)

  def __getitem__(self, key):
    if key in ("_dict_stack", "__name__"):
      # Disallow config script from accessing internal members
      logger.warning("Config illegal attempt to access %s", key)
      return None

    if key == "__file__":
      # Allow config script to access __file__
      return self.filepath

    if hasattr(self, key):
      # Allow config script to access section(), push_section(), pop_section()
      # directly
      return getattr(self, key)

    # Check if any nested scopes contain this name, and return it if they do.
    # this means that sections are "scoped".
    for dictitem in reversed(self._dict_stack):
      if key in dictitem:
        return dictitem[key]

    # Otherwise act like a dictionary
    return super(ExecGlobal, self).__getitem__(key)

  def __setitem__(self, key, value):
    if self._dict_stack:
      self._dict_stack[-1][key] = value
    else:
      super(ExecGlobal, self).__setitem__(key, value)



class ConfigObject(object):
  """
  Base class for encapsulationg options/parameters
  """

  # TODO(josh): merge all of the following into an ordered list of named tuples
  # containing (name, default_value, choices, vardocs). Then replace all of the
  # self.<name> = assignments with an iteration over the list

  # Map group name to list of fields
  _group_map = {}

  # Additional fields not listed in __init__
  _extra_fields = []

  # Additinal help text
  _vardocs = {}

  @classmethod
  def get_init_names(cls):
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

  @classmethod
  def get_field_names(cls):
    return cls.get_init_names() + cls._extra_fields

  def iter_fields(self):
    for fieldname in self.get_field_names():
      yield (fieldname, getattr(self, fieldname))

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
    groups = collections.OrderedDict()

    # Invert the group map
    group_map = {}
    default_group = ""
    for key, fieldlist in self._group_map:
      if not fieldlist:
        default_group = key
      for field in fieldlist:
        group_map[field] = key

    for field in self.get_field_names():
      groupname = groups.get(field, default_group)
      if groupname not in groups:
        groups[groupname] = []
      group = groups[groupname]
      group.append((field, serialize(getattr(self, field))))

    out = collections.OrderedDict()
    out["_comment"] = self.__doc__
    for idx, (title, fields) in enumerate(groups.items()):
      if with_comments:
        out["_group{:02d}".format(idx)] = title
      out.update(fields)

    return out

  def _dump_fields(self, outfile, fieldnames, depth):
    indent = "  " * depth
    linewidth = 80 - len(indent) - len("# ")

    ppr = pprint.PrettyPrinter(indent=2)
    for fieldname in fieldnames:
      value = getattr(self, fieldname)
      helptext = self._vardocs.get(fieldname, None)
      if helptext:
        for line in textwrap.wrap(helptext, linewidth):
          outfile.write(indent)
          outfile.write('# {}\n'.format(line.rstrip()))
      if isinstance(value, ConfigObject):
        if value.__doc__:
          section_doc_lines = value.__doc__.split("\n")
          ruler_len = max(len(line) for line in section_doc_lines)
          outfile.write("# {}\n".format("-" * ruler_len))
          for line in section_doc_lines:
            outfile.write(indent)
            outfile.write('# {}\n'.format(line.rstrip()))
          outfile.write("# {}\n".format("-" * ruler_len))

        outfile.write(indent)
        outfile.write("with section(\"{}\"):\n".format(fieldname))
        value.dump(outfile, depth + 1)
      else:
        pretty = "{} = {}".format(fieldname, ppr.pformat(value))
        for line in pretty.split("\n"):
          outfile.write(indent)
          outfile.write(line)
          outfile.write("\n")
        outfile.write("\n")


  def dump(self, outfile, depth=0):
    group_map = [(key, value) for key, value in self._group_map]

    if not group_map:
      self._dump_fields(outfile, self.get_field_names(), depth)
      return

    # Populate the default group
    default_group = []
    filed_fieldnames = set()
    for _, fieldlist in group_map:
      for fieldname in fieldlist:
        filed_fieldnames.add(fieldname)
      if not fieldlist:
        default_group = fieldlist

    # Construct the default group
    for fieldname in self.get_field_names():
      if fieldname in filed_fieldnames:
        continue
      default_group.append(fieldname)

    for group_title, fieldnames in group_map:
      outfile.write("# ")
      outfile.write("-" * len(group_title))
      outfile.write("\n")
      outfile.write("# ")
      outfile.write(group_title)
      outfile.write("\n")
      outfile.write("# ")
      outfile.write("-" * len(group_title))
      outfile.write("\n")
      self._dump_fields(outfile, fieldnames, depth)


  def clone(self):
    """
    Return a copy of self.
    """
    return self.__class__(**self.as_dict())
