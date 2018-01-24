"""
Command specifications for cmake built-in commands.
"""

ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'


def decl_command(fn_spec, command_name, pargs=None, flags=None, kwargs=None):
  if pargs is None:
    pargs = 0
  if flags is None:
    flags = []
  if kwargs is None:
    kwargs = {}

  decl = dict(kwargs)
  decl['pargs'] = pargs
  for flag in flags:
    decl[flag] = 0
  fn_spec[command_name] = decl


def get_fn_spec():
  """
  Return a dictionary mapping cmake function names to a dictionary containing
  kwarg specifications.
  """

  fn_spec = {}

  decl_command(fn_spec, "add_custom_command", flags=["APPEND", "VERBATIM"],
               kwargs={"COMMAND": ONE_OR_MORE,
                       "COMMENT": ZERO_OR_MORE,
                       "DEPENDS": ZERO_OR_MORE,
                       "IMPLICIT_DEPENDS": ZERO_OR_MORE,
                       "MAIN_DEPENDENCY": 1,
                       "OUTPUT": ONE_OR_MORE,
                       "WORKING_DIRECTORY": 1
                       })  # pylint: disable=bad-continuation

  decl_command(fn_spec, "add_custom_target", flags=["ALL", "VERBATIM"],
               kwargs={"COMMAND": ZERO_OR_MORE,
                       "COMMENT": ZERO_OR_MORE,
                       "DEPENDS": ZERO_OR_MORE,
                       "SOURCES": ZERO_OR_MORE,
                       "WORKING_DIRECTORY": ZERO_OR_MORE
                       })  # pylint: disable=bad-continuation

  decl_command(fn_spec, "add_executable",
               flags=["EXCLUDE_FROM_ALL", "MACOSX_BUNDLE",
                      "WIN32"], kwargs={})

  decl_command(fn_spec, "add_library",
               flags=["EXCLUDE_FROM_ALL", "MODULE", "SHARED", "STATIC"],
               kwargs={})

  decl_command(fn_spec, "add_test", flags=[], kwargs={
      "COMMAND": ZERO_OR_MORE,
      "CONFIGURATIONS": ZERO_OR_MORE,
      "NAME": ZERO_OR_MORE,
      "WORKING_DIRECTORY": ZERO_OR_MORE
  })

  decl_command(fn_spec, "cmake_host_system_information", flags=[], kwargs={
      "QUERY": ZERO_OR_MORE,
      "RESULT": ZERO_OR_MORE
  })

  decl_command(fn_spec, "cmake_minimum_required",
               flags=["FATAL_ERROR"], kwargs={})

  decl_command(fn_spec, "cmake_minimum_required_version", flags=[], kwargs={
      "VERSION": ZERO_OR_MORE
  })

  decl_command(fn_spec, "configure_file",
               flags=["@ONLY", "COPYONLY", "ESCAPE_QUOTES"],
               kwargs={"NEWLINE_STYLE": ZERO_OR_MORE})

  decl_command(fn_spec, "define_property",
               flags=["CACHED_VARIABLE", "DIRECTORY", "GLOBAL", "INHERITED",
                      "SOURCE", "TARGET", "TEST", "VARIABLE"],
               kwargs={
                   "BRIEF_DOCS": ZERO_OR_MORE,
                   "FULL_DOCS": ZERO_OR_MORE,
                   "PROPERTY": ZERO_OR_MORE
               })

  decl_command(fn_spec, "enable_language", flags=["OPTIONAL"], kwargs={})

  decl_command(fn_spec, "execute_process",
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

  decl_command(fn_spec, "file",
               flags=["FOLLOW_SYMLINKS", "GENERATE", "HEX", "NEWLINE_CONSUME",
                      "NO_HEX_CONVERSION", "SHOW_PROGRESS", "UTC"],
               kwargs={
                   "APPEND": ZERO_OR_MORE,
                   "DOWNLOAD": ZERO_OR_MORE,
                   "EXPECTED_HASH": ZERO_OR_MORE,
                   "EXPECTED_MD5": ZERO_OR_MORE,
                   "GLOB": ZERO_OR_MORE,
                   "GLOB_RECURSE": ZERO_OR_MORE,
                   "INACTIVITY_TIMEOUT": ZERO_OR_MORE,
                   "LENGTH_MAXIMUM": ZERO_OR_MORE,
                   "LENGTH_MINIMUM": ZERO_OR_MORE,
                   "LIMIT": ZERO_OR_MORE,
                   "LIMIT_COUNT": ZERO_OR_MORE,
                   "LIMIT_INPUT": ZERO_OR_MORE,
                   "LIMIT_OUTPUT": ZERO_OR_MORE,
                   "LOG": ZERO_OR_MORE,
                   "MAKE_DIRECTORY": ZERO_OR_MORE,
                   "MD5": ZERO_OR_MORE,
                   "OFFSET": ZERO_OR_MORE,
                   "OUTPUTINPUTCONTENTCONDITION": ZERO_OR_MORE,
                   "READ": ZERO_OR_MORE,
                   "REGEX": ZERO_OR_MORE,
                   "RELATIVE": ZERO_OR_MORE,
                   "RELATIVE_PATH": ZERO_OR_MORE,
                   "REMOVE": ZERO_OR_MORE,
                   "REMOVE_RECURSE": ZERO_OR_MORE,
                   "RENAME": ZERO_OR_MORE,
                   "SHA1": ZERO_OR_MORE,
                   "SHA256": ZERO_OR_MORE,
                   "SHA384": ZERO_OR_MORE,
                   "SHA512": ZERO_OR_MORE,
                   "STATUS": ZERO_OR_MORE,
                   "STRINGS": ZERO_OR_MORE,
                   "TIMEOUT": ZERO_OR_MORE,
                   "TIMESTAMP": ZERO_OR_MORE,
                   "TLS_CAINFO": ZERO_OR_MORE,
                   "TLS_VERIFY": ZERO_OR_MORE,
                   "TO_CMAKE_PATH": ZERO_OR_MORE,
                   "TO_NATIVE_PATH": ZERO_OR_MORE,
                   "UPLOAD": ZERO_OR_MORE,
                   "WRITE": ZERO_OR_MORE
               })

  decl_command(fn_spec, "find_file",
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

  decl_command(fn_spec, "find_library",
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

  decl_command(fn_spec, "find_package",
               flags=["EXACT", "MODULEREQUIREDNO_POLICY_SCOPE", "QUIET"],
               kwargs={
                   "COMPONENTS": ZERO_OR_MORE,
                   "OPTIONAL_COMPONENTS": ZERO_OR_MORE
               })

  decl_command(fn_spec, "find_path",
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

  decl_command(fn_spec, "find_program",
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

  decl_command(fn_spec, "get_directory_property", flags=[], kwargs={
      "DIRECTORY": ZERO_OR_MORE
  })

  decl_command(fn_spec, "get_property",
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

  decl_command(fn_spec, "include",
               flags=["NO_POLICY_SCOPE", "OPTIONAL"],
               kwargs={"RESULT_VARIABLE": ZERO_OR_MORE})

  decl_command(fn_spec, "include_directories",
               flags=["AFTER", "BEFORE", "SYSTEM"], kwargs={})

  decl_command(fn_spec, "install",
               flags=["NAMELINK_ONLY", "NAMELINK_SKIP", "OPTIONAL",
                      "USE_SOURCE_PERMISSIONS"],
               kwargs={
                   "ARCHIVE": ZERO_OR_MORE,
                   "BUNDLE": ZERO_OR_MORE,
                   "COMPONENT": ZERO_OR_MORE,
                   "CONFIGURATIONS": ZERO_OR_MORE,
                   "DIRECTORY": ZERO_OR_MORE,
                   "DIRECTORY_PERMISSIONS": ZERO_OR_MORE,
                   "EXPORT": ZERO_OR_MORE,
                   "FILES": ZERO_OR_MORE,
                   "FILES_MATCHING": ZERO_OR_MORE,
                   "FILE_PERMISSIONS": ZERO_OR_MORE,
                   "FRAMEWORK": ZERO_OR_MORE,
                   "INCLUDESPERMISSIONS": ZERO_OR_MORE,
                   "LIBRARY": ZERO_OR_MORE,
                   "PRIVATE_HEADER": ZERO_OR_MORE,
                   "PROGRAMS": ZERO_OR_MORE,
                   "PUBLIC_HEADER": ZERO_OR_MORE,
                   "RENAME": ZERO_OR_MORE,
                   "RESOURCE": ZERO_OR_MORE,
                   "RUNTIME": ZERO_OR_MORE,
                   "TARGETS": ZERO_OR_MORE
               })

  decl_command(fn_spec, "list", flags=[], kwargs={
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

  decl_command(fn_spec, "mark_as_advanced", flags=["CLEAR", "FORCE"], kwargs={})

  decl_command(fn_spec, "message", flags=[], kwargs={
      "AUTHOR_WARNING": ZERO_OR_MORE,
      "DEPRECATION": ZERO_OR_MORE,
      "FATAL_ERROR": ZERO_OR_MORE,
      "SEND_ERROR": ZERO_OR_MORE,
      "STATUS": ZERO_OR_MORE,
      "WARNING": ZERO_OR_MORE
  })

  decl_command(fn_spec, "project", flags=[], kwargs={
      "LANGUAGES": ZERO_OR_MORE,
      "VERSION": ZERO_OR_MORE
  })

  decl_command(fn_spec, "set", flags=["FORCE", "PARENT_SCOPE"], kwargs={
      "CACHE": ZERO_OR_MORE
  })

  decl_command(fn_spec, "set_directory_properties", flags=[], kwargs={
      "PROPERTIES": ZERO_OR_MORE
  })

  decl_command(fn_spec, "set_property",
               flags=["APPEND", "APPEND_STRING", "GLOBAL"],
               kwargs={
                   "CACHE": ZERO_OR_MORE,
                   "DIRECTORY": ZERO_OR_MORE,
                   "PROPERTY": ZERO_OR_MORE,
                   "SOURCE": ZERO_OR_MORE,
                   "TARGET": ZERO_OR_MORE,
                   "TEST": ZERO_OR_MORE
               })

  decl_command(fn_spec, "set_target_properties", pargs=ZERO_OR_MORE, flags=[],
               kwargs={"PROPERTIES": ZERO_OR_MORE})

  decl_command(fn_spec, "set_tests_properties", flags=[], kwargs={
      "PROPERTIES": ZERO_OR_MORE
  })

  decl_command(fn_spec, "string",
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

  decl_command(fn_spec, "try_compile", flags=[], kwargs={
      "CMAKE_FLAGS": ZERO_OR_MORE,
      "COMPILE_DEFINITIONS": ZERO_OR_MORE,
      "COPY_FILE": ZERO_OR_MORE,
      "LINK_LIBRARIES": ZERO_OR_MORE,
      "OUTPUT_VARIABLE": ZERO_OR_MORE,
      "RESULT_VAR": ZERO_OR_MORE
  })

  decl_command(fn_spec, "try_run", flags=[], kwargs={
      "ARGS": ZERO_OR_MORE,
      "CMAKE_FLAGS": ZERO_OR_MORE,
      "COMPILE_DEFINITIONS": ZERO_OR_MORE,
      "COMPILE_OUTPUT_VARIABLE": ZERO_OR_MORE,
      "OUTPUT_VARIABLE": ZERO_OR_MORE,
      "RUN_OUTPUT_VARIABLE": ZERO_OR_MORE
  })

  return fn_spec
