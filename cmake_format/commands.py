"""
Command specifications for cmake built-in commands.
"""

from __future__ import unicode_literals
import sys

ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'

if sys.version_info[0] < 3:
  STRING_TYPES = (str, unicode)
else:
  STRING_TYPES = (str,)

CONDITIONAL_FLAGS = [
    "COMMAND",
    "DEFINED",
    "EQUAL",
    "EXISTS",
    "GREATER",
    "LESS",
    "IS_ABSOLUTE",
    "IS_DIRECTORY",
    "IS_NEWER_THAN",
    "IS_SYMLINK",
    "MATCHES",
    "NOT",
    "POLICY",
    "STRLESS",
    "STRGREATER",
    "STREQUAL",
    "TARGET",
    "TEST",
    "VERSION_EQUAL",
    "VERSION_GREATER",
    "VERSION_LESS",
]

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


def make_conditional_spec(name=None):
  if name is None:
    name = '<conditional>'
  flags = list(CONDITIONAL_FLAGS)
  spec = CommandSpec(name, pargs='+', flags=list(flags))
  return CommandSpec(name, pargs='+', flags=list(flags),
                     kwargs={'AND': spec, 'OR': spec})


class CommandSpec(dict):
  """
  A command specification is primarily a dictionary mapping keyword arguments
  to command specifications. It also includes a command name and number of
  positional arguments
  """

  def __init__(self, name, pargs=None, flags=None, kwargs=None):
    super(CommandSpec, self).__init__()
    if sys.version_info[0] < 3:
      scalar_types = (int,) + STRING_TYPES
    else:
      scalar_types = (int, str)

    if pargs is None:
      pargs = ZERO_OR_MORE

    if flags is None:
      flags = []

    self.name = name
    self.pargs = pargs

    for flagname in flags:
      self[flagname] = 0

    self.flags = list(flags)

    if kwargs is not None:
      if isinstance(kwargs, dict):
        items = kwargs.items()
      elif isinstance(kwargs, (list, tuple)):
        items = list(kwargs)

      for keyword, spec in items:
        if isinstance(spec, scalar_types):
          self[keyword] = spec
        elif isinstance(spec, CommandSpec):
          self[keyword] = spec
        elif isinstance(spec, dict):
          self[keyword] = CommandSpec(name=keyword, **spec)
        else:
          raise ValueError("Unexpected type '{}' for kwargs"
                           .format(type(kwargs)))

  def is_flag(self, key):
    return self.get(key, None) == 0

  def is_kwarg(self, key):
    subspec = self.get(key, None)
    if subspec is None:
      return False
    if isinstance(subspec, int):
      return subspec != 0
    if isinstance(subspec, STRING_TYPES + (CommandSpec,)):
      return True
    raise ValueError("Unexpected kwargspec for {}: {}"
                     .format(key, type(subspec)))

  def add(self, name, pargs=None, flags=None, kwargs=None):
    self[name.lower()] = CommandSpec(name, pargs, flags, kwargs)

  def add_conditional(self, name):
    self[name.lower()] = make_conditional_spec(name)


def get_fn_spec():
  """
  Return a dictionary mapping cmake function names to a dictionary containing
  kwarg specifications.
  """

  fn_spec = CommandSpec('<root>')

  fn_spec.add(
      "add_test",
      flags=[],
      kwargs={
          "COMMAND": dict(
              pargs=ONE_OR_MORE,
              kwargs=[('ARGS', ZERO_OR_MORE)]
          ),
          "CONFIGURATIONS": ZERO_OR_MORE,
          "NAME": ZERO_OR_MORE,
          "WORKING_DIRECTORY": ZERO_OR_MORE
      })

  fn_spec.add(
      "cmake_host_system_information",
      flags=[],
      kwargs={
          "QUERY": ZERO_OR_MORE,
          "RESULT": ZERO_OR_MORE
      })

  fn_spec.add(
      "cmake_minimum_required",
      flags=["FATAL_ERROR"],
      kwargs={"VERSION": ZERO_OR_MORE})

  fn_spec.add(
      "cmake_minimum_required_version",
      flags=[],
      kwargs={"VERSION": ZERO_OR_MORE})

  fn_spec.add(
      "configure_file",
      flags=["@ONLY", "COPYONLY", "ESCAPE_QUOTES"],
      kwargs={"NEWLINE_STYLE": ZERO_OR_MORE})

  fn_spec.add(
      "define_property",
      flags=["CACHED_VARIABLE", "DIRECTORY", "GLOBAL", "INHERITED",
             "SOURCE", "TARGET", "TEST", "VARIABLE"],
      kwargs={
          "BRIEF_DOCS": ZERO_OR_MORE,
          "FULL_DOCS": ZERO_OR_MORE,
          "PROPERTY": ZERO_OR_MORE
      })

  fn_spec.add(
      "enable_language",
      flags=["OPTIONAL"],
      kwargs={})

  fn_spec.add(
      "execute_process",
      flags=["ERROR_QUIET", "ERROR_STRIP_TRAILING_WHITESPACE",
             "OUTPUT_QUIET", "OUTPUT_STRIP_TRAILING_WHITESPACE"],
      kwargs={
          "COMMAND": ZERO_OR_MORE,
          "ERROR_FILE": ZERO_OR_MORE,
          "ERROR_VARIABLE": ZERO_OR_MORE,
          "INPUT_FILE": ZERO_OR_MORE,
          "OUTPUT_FILE": ZERO_OR_MORE,
          "OUTPUT_VARIABLE": ZERO_OR_MORE,
          "RESULT_VARIABLE": ZERO_OR_MORE,
          "TIMEOUT": ZERO_OR_MORE,
          "WORKING_DIRECTORY": ZERO_OR_MORE
      })

  fn_spec.add(
      "export",
      flags=["APPEND", "EXPORT_LINK_INTERFACE_LIBRARIES"],
      kwargs={
          "ANDROID_MK": 1,
          "EXPORT": 1,
          "FILE": 1,
          "NAMESPACE": 1,
          "PACKAGE": 1,
          "TARGETS": ONE_OR_MORE
      })

  fn_spec.add(
      "find_file",
      flags=["CMAKE_FIND_ROOT_PATH_BOTH", "NO_CMAKE_ENVIRONMENT_PATH",
             "NO_CMAKE_FIND_ROOT_PATH", "NO_CMAKE_PATH",
             "NO_CMAKE_SYSTEM_PATH", "NO_DEFAULT_PATH",
             "NO_SYSTEM_ENVIRONMENT_PATH",
             "ONLY_CMAKE_FIND_ROOT_PATH"],
      kwargs={
          "DOC": ZERO_OR_MORE,
          "HINTS": ZERO_OR_MORE,
          "NAMES": ZERO_OR_MORE,
          "PATHS": ZERO_OR_MORE,
          "PATH_SUFFIXES": ZERO_OR_MORE
      })

  fn_spec.add(
      "find_library",
      flags=["CMAKE_FIND_ROOT_PATH_BOTH", "NO_CMAKE_ENVIRONMENT_PATH",
             "NO_CMAKE_FIND_ROOT_PATH", "NO_CMAKE_PATH",
             "NO_CMKE_SYSTEM_PATH", "NO_DEFAULT_PATH",
             "NO_SYSTEM_ENVIRONMENT_PATH",
             "ONLY_CMAKE_FIND_ROOT_PATH"],
      kwargs={
          "DOC": ZERO_OR_MORE,
          "HINTS": ZERO_OR_MORE,
          "NAMES": ZERO_OR_MORE,
          "PATHS": ZERO_OR_MORE,
          "PATH_SUFFIXES": ZERO_OR_MORE
      })

  fn_spec.add(
      "find_package",
      pargs=ZERO_OR_MORE,
      flags=["EXACT", "MODULE", "REQUIRED", "NO_POLICY_SCOPE", "QUIET"],
      kwargs={
          "COMPONENTS": ZERO_OR_MORE,
          "OPTIONAL_COMPONENTS": ZERO_OR_MORE
      })

  fn_spec.add(
      "find_path",
      flags=["CMAKE_FIND_ROOT_PATH_BOTH", "NO_CMAKE_ENVIRONMENT_PATH",
             "NO_CMAKE_FIND_ROOT_PATH", "NO_CMAKE_PATH",
             "NO_CMKE_SYSTEM_PATH", "NO_DEFAULT_PATH",
             "NO_SYSTEM_ENVIRONMENT_PATH",
             "ONLY_CMAKE_FIND_ROOT_PATH"],
      kwargs={
          "DOC": ZERO_OR_MORE,
          "HINTS": ZERO_OR_MORE,
          "NAMES": ZERO_OR_MORE,
          "PATHS": ZERO_OR_MORE,
          "PATH_SUFFIXES": ZERO_OR_MORE
      })

  fn_spec.add(
      "find_program",
      flags=["CMAKE_FIND_ROOT_PATH_BOTH", "NO_CMAKE_ENVIRONMENT_PATH",
             "NO_CMAKE_FIND_ROOT_PATH", "NO_CMAKE_PATH",
             "NO_CMAKE_SYSTEM_PATH", "NO_DEFAULT_PATH",
             "NO_SYSTEM_ENVIRONMENT_PATH",
             "ONLY_CMAKE_FIND_ROOT_PATH"],
      kwargs={
          "DOC": ZERO_OR_MORE,
          "HINTS": ZERO_OR_MORE,
          "NAMES": ZERO_OR_MORE,
          "PATHS": ZERO_OR_MORE,
          "PATH_SUFFIXES": ZERO_OR_MORE
      })

  fn_spec.add(
      "get_directory_property", flags=[], kwargs={
          "DIRECTORY": ZERO_OR_MORE
      })

  fn_spec.add(
      "get_property",
      flags=["BRIEF_DOCS", "DEFINED", "FULL_DOCS", "GLOBAL", "SET",
             "VARIABLE"],
      kwargs={
          "CACHE": ZERO_OR_MORE,
          "DIRECTORY": ZERO_OR_MORE,
          "PROPERTY": ZERO_OR_MORE,
          "SOURCE": ZERO_OR_MORE,
          "TARGET": ZERO_OR_MORE,
          "TEST": ZERO_OR_MORE
      })

  fn_spec.add(
      "include",
      flags=["NO_POLICY_SCOPE", "OPTIONAL"],
      kwargs={"RESULT_VARIABLE": ZERO_OR_MORE})

  fn_spec.add(
      "include_directories",
      flags=["AFTER", "BEFORE", "SYSTEM"], kwargs={})

  fn_spec.add(
      "list", flags=[], kwargs={
          "APPEND": ZERO_OR_MORE,
          "FIND": ZERO_OR_MORE,
          "GET": ZERO_OR_MORE,
          "INSERT": ZERO_OR_MORE,
          "LENGTH": ZERO_OR_MORE,
          "REMOVE_AT": ZERO_OR_MORE,
          "REMOVE_DUPLICATES": ZERO_OR_MORE,
          "REMOVE_ITEM": ZERO_OR_MORE,
          "REVERSE": ZERO_OR_MORE,
          "SORT": ZERO_OR_MORE
      })

  fn_spec.add(
      "mark_as_advanced", flags=["CLEAR", "FORCE"], kwargs={})

  fn_spec.add(
      "message", flags=[], kwargs={
          "AUTHOR_WARNING": ZERO_OR_MORE,
          "DEPRECATION": ZERO_OR_MORE,
          "FATAL_ERROR": ZERO_OR_MORE,
          "SEND_ERROR": ZERO_OR_MORE,
          "STATUS": ZERO_OR_MORE,
          "WARNING": ZERO_OR_MORE
      })

  fn_spec.add(
      "project", flags=[], kwargs={
          "DESCRIPTION": 1,
          "HOMEPAGE_URL": 1,
          "LANGUAGES": ZERO_OR_MORE,
          "VERSION": ZERO_OR_MORE,
      })

  fn_spec.add(
      "set_directory_properties", flags=[], kwargs={
          "PROPERTIES": ZERO_OR_MORE
      })

  fn_spec.add(
      "set_property",
      flags=["APPEND", "APPEND_STRING", "GLOBAL"],
      kwargs={
          "CACHE": ZERO_OR_MORE,
          "DIRECTORY": ZERO_OR_MORE,
          "PROPERTY": ZERO_OR_MORE,
          "SOURCE": ZERO_OR_MORE,
          "TARGET": ZERO_OR_MORE,
          "TEST": ZERO_OR_MORE
      })

  fn_spec.add(
      "set_tests_properties", flags=[], kwargs={
          "PROPERTIES": ZERO_OR_MORE
      })

  fn_spec.add(
      "string",
      flags=["@ONLY", "ESCAPE_QUOTES", "REVERSE", "UTC"],
      kwargs={
          "ALPHABET": ZERO_OR_MORE,
          "ASCII": ZERO_OR_MORE,
          "COMPARE": ZERO_OR_MORE,
          "CONCAT": ZERO_OR_MORE,
          "CONFIGURE": ZERO_OR_MORE,
          "FIND": ZERO_OR_MORE,
          "LENGTH": ZERO_OR_MORE,
          "MAKE_C_IDENTIFIER": ZERO_OR_MORE,
          "MD5": ZERO_OR_MORE,
          "RANDOM": ZERO_OR_MORE,
          "RANDOM_SEED": ZERO_OR_MORE,
          "REGEX": ZERO_OR_MORE,
          "REPLACE": ZERO_OR_MORE,
          "SHA1": ZERO_OR_MORE,
          "SHA256": ZERO_OR_MORE,
          "SHA384": ZERO_OR_MORE,
          "SHA512": ZERO_OR_MORE,
          "STRIP": ZERO_OR_MORE,
          "SUBSTRING": ZERO_OR_MORE,
          "TIMESTAMP": ZERO_OR_MORE,
          "TOLOWER": ZERO_OR_MORE,
          "TOUPPER": ZERO_OR_MORE
      })

  fn_spec.add(
      "try_compile", flags=[], kwargs={
          "CMAKE_FLAGS": ZERO_OR_MORE,
          "COMPILE_DEFINITIONS": ZERO_OR_MORE,
          "COPY_FILE": ZERO_OR_MORE,
          "LINK_LIBRARIES": ZERO_OR_MORE,
          "OUTPUT_VARIABLE": ZERO_OR_MORE,
          "RESULT_VAR": ZERO_OR_MORE
      })

  fn_spec.add(
      "target_compile_options", flags=[], kwargs={
          "PRIVATE": ONE_OR_MORE,
          "PUBLIC": ONE_OR_MORE,
          "INTERFACE": ONE_OR_MORE
      })

  fn_spec.add(
      "target_include_directories", flags=[], kwargs={
          "PRIVATE": ONE_OR_MORE,
          "PUBLIC": ONE_OR_MORE,
          "INTERFACE": ONE_OR_MORE
      })

  fn_spec.add(
      "target_link_libraries", flags=[], kwargs={
          "PRIVATE": ONE_OR_MORE,
          "PUBLIC": ONE_OR_MORE,
          "INTERFACE": ONE_OR_MORE
      })

  fn_spec.add(
      "try_run", flags=[], kwargs={
          "ARGS": ZERO_OR_MORE,
          "CMAKE_FLAGS": ZERO_OR_MORE,
          "COMPILE_DEFINITIONS": ZERO_OR_MORE,
          "COMPILE_OUTPUT_VARIABLE": ZERO_OR_MORE,
          "OUTPUT_VARIABLE": ZERO_OR_MORE,
          "RUN_OUTPUT_VARIABLE": ZERO_OR_MORE
      })

  # fn_spec.add_conditional("if")
  # fn_spec.add_conditional("elseif")
  # fn_spec.add_conditional("while")

  # TODO(josh): should this be user-enabled? Maybe some kind of plugin/extension
  # system?
  add_standard_nonbuiltins(fn_spec)

  return fn_spec


def add_standard_nonbuiltins(fn_spec):
  """
  Add commands provided by "standard" listfiles
  """

  fn_spec.add(
      "write_basic_package_version_file", flags=[], kwargs={
          "COMPATIBILITY": 1,
          "VERSION": 1
      })
