"""
Command specifications for cmake built-in commands.
"""

from __future__ import unicode_literals
import sys

from cmake_format.common import UserError
from cmake_format.parse.util import PositionalSpec
from cmake_format.parse_funs import standard_builtins, standard_modules

ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'

if sys.version_info[0] < 3:
  STRING_TYPES = (str, unicode)
else:
  STRING_TYPES = (str,)


CANONICAL_SPELLINGS = {
    "FetchContent_Declare",
    "FetchContent_MakeAvailable",
    "FetchContent_GetProperties",
    "FetchContent_Populate",
    "ExternalProject_Add",
    "ExternalProject_Add_Step",
    "ExternalProject_Add_StepDependencies",
    "ExternalProject_Add_StepTargets",
    "ExternalProject_Get_Property",
}


def get_default_config():
  """
  Return the default per-command configuration database
  """
  per_command = {}
  for spelling in CANONICAL_SPELLINGS:
    per_command[spelling.lower()] = {
        "spelling": spelling
    }

  return per_command


def parse_pspec(pargs, flags):
  """
  Parse a positional argument specification.
  """
  out = []

  # Default pargs is "*"
  if pargs is None:
    pargs = ZERO_OR_MORE

  # If we only have one scalar specification, return a legacy specification
  if isinstance(pargs, STRING_TYPES + (int,)):
    return [PositionalSpec(pargs, flags=flags, legacy=True)]

  if flags:
    raise UserError(
        "Illegal use of top-level 'flags' keyword with new-style positional"
        " argument declaration")

  # If we only have one dictionary specification, then put it in a dictionary
  # so that we can do the rest consistently
  if isinstance(pargs, dict):
    pargs = [pargs]

  for pargdecl in pargs:
    if isinstance(pargdecl, STRING_TYPES + (int,)):
      # A scalar declaration is interpreted as npargs
      out.append(PositionalSpec(pargdecl))
      continue

    if isinstance(pargdecl, dict):
        # A dictionary is interpreted as init kwargs
      if "npargs" not in pargdecl:
        pargdecl = dict(pargdecl)
        pargdecl["nargs"] = ZERO_OR_MORE
      out.append(PositionalSpec(**pargdecl))
      continue

    if isinstance(pargdecl, (list, tuple)):
        # A list or tuple is interpreted as (*args, [kwargs])
      args = list(pargdecl)
      kwargs = {}
      if isinstance(args[-1], dict):
        kwargs = args.pop(-1)
      out.append(PositionalSpec(*args, **kwargs))

  return out


class CommandSpec(object):
  """
  A command specification is primarily a dictionary mapping keyword arguments
  to command specifications. It also includes a command name and number of
  positional arguments
  """

  def __init__(self, name, pargs=None, flags=None, kwargs=None, spelling=None):
    super(CommandSpec, self).__init__()
    scalar_types = (int,) + STRING_TYPES

    self.name = name
    self.spelling = spelling
    if spelling is None:
      self.spelling = name

    try:
      self.pargs = parse_pspec(pargs, flags)
    except (TypeError, UserError) as ex:
      message = (
          "Invalid user-supplied specification for positional arguments of "
          "{}:\n{}".format(name, ex))
      raise UserError(message)

    self.kwargs = {}

    if kwargs is not None:
      if isinstance(kwargs, dict):
        items = kwargs.items()
      elif isinstance(kwargs, (list, tuple)):
        items = list(kwargs)
      else:
        raise ValueError(
            "Invalid type {} for kwargs of {}: {}"
            .format(type(kwargs), name, kwargs))

      for keyword, spec in items:
        if isinstance(spec, scalar_types):
          self.kwargs[keyword] = CommandSpec(name=keyword, pargs=spec)
        elif isinstance(spec, CommandSpec):
          self.kwargs[keyword] = spec
        elif isinstance(spec, dict):
          self.kwargs[keyword] = CommandSpec(name=keyword, **spec)
        else:
          raise ValueError("Unexpected type '{}' for kwargs"
                           .format(type(kwargs)))

  def is_flag(self, key):
    return self.kwargs.get(key, None) == 0

  def is_kwarg(self, key):
    subspec = self.kwargs.get(key, None)
    if subspec is None:
      return False
    if isinstance(subspec, int):
      return subspec != 0
    if isinstance(subspec, STRING_TYPES + (CommandSpec,)):
      return True
    raise ValueError("Unexpected kwargspec for {}: {}"
                     .format(key, type(subspec)))

  def add(self, name, pargs=None, flags=None, kwargs=None, spelling=None):
    self.kwargs[name.lower()] = CommandSpec(
        name, pargs, flags, kwargs, spelling)


def get_fn_spec():
  """
  Return a dictionary mapping cmake function names to a dictionary containing
  kwarg specifications.
  """

  fn_spec = CommandSpec('<root>')
  for grouping in (standard_builtins, standard_modules):
    for funname, spec in sorted(grouping.FUNSPECS.items()):
      fn_spec.add(funname, **spec)
  return fn_spec


# pylint: disable=bad-continuation
# pylint: disable=too-many-lines
