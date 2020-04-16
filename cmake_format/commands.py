"""
Command specifications for cmake built-in commands.
"""

from __future__ import unicode_literals
import sys

from cmake_format.common import UserError
from cmake_format.parse.util import PositionalSpec

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
  for grouping in (BUILTINS, GENERATED_FROM_MODULES):
    for funname, spec in sorted(grouping.items()):
      fn_spec.add(funname, **spec)
  return fn_spec


# pylint: disable=bad-continuation
# pylint: disable=too-many-lines
BUILTINS = {
  "add_test": {
    "kwargs": {
      "COMMAND": {
        "pargs": "+",
        "kwargs": {
          "ARGS": "*"
        }
      },
      "CONFIGURATIONS": "*",
      "NAME": "*",
      "WORKING_DIRECTORY": "*"
    }
  },
  "cmake_host_system_information": {
    "kwargs": {
      "QUERY": "*",
      "RESULT": "*"
    }
  },
  "cmake_minimum_required": {
    "flags": [
      "FATAL_ERROR"
    ],
    "kwargs": {
      "VERSION": "*"
    }
  },
  "cmake_minimum_required_version": {
    "kwargs": {
      "VERSION": "*"
    }
  },
  "configure_file": {
    "flags": [
      "@ONLY",
      "COPYONLY",
      "ESCAPE_QUOTES"
    ],
    "kwargs": {
      "NEWLINE_STYLE": "*"
    }
  },
  "define_property": {
    "flags": [
      "CACHED_VARIABLE",
      "DIRECTORY",
      "GLOBAL",
      "INHERITED",
      "SOURCE",
      "TARGET",
      "TEST",
      "VARIABLE"
    ],
    "kwargs": {
      "BRIEF_DOCS": "*",
      "FULL_DOCS": "*",
      "PROPERTY": "*"
    }
  },
  "enable_language": {
    "flags": [
      "OPTIONAL"
    ],
    "kwargs": {}
  },
  "execute_process": {
    "flags": [
      "ERROR_QUIET",
      "ERROR_STRIP_TRAILING_WHITESPACE",
      "OUTPUT_QUIET",
      "OUTPUT_STRIP_TRAILING_WHITESPACE"
    ],
    "kwargs": {
      "COMMAND": "*",
      "ERROR_FILE": "*",
      "ERROR_VARIABLE": "*",
      "INPUT_FILE": "*",
      "OUTPUT_FILE": "*",
      "OUTPUT_VARIABLE": "*",
      "RESULT_VARIABLE": "*",
      "TIMEOUT": "*",
      "WORKING_DIRECTORY": "*"
    }
  },
  "export": {
    "flags": [
      "APPEND",
      "EXPORT_LINK_INTERFACE_LIBRARIES"
    ],
    "kwargs": {
      "ANDROID_MK": 1,
      "EXPORT": 1,
      "FILE": 1,
      "NAMESPACE": 1,
      "PACKAGE": 1,
      "TARGETS": "+"
    }
  },
  "find_file": {
    "flags": [
      "CMAKE_FIND_ROOT_PATH_BOTH",
      "NO_CMAKE_ENVIRONMENT_PATH",
      "NO_CMAKE_FIND_ROOT_PATH",
      "NO_CMAKE_PATH",
      "NO_CMAKE_SYSTEM_PATH",
      "NO_DEFAULT_PATH",
      "NO_SYSTEM_ENVIRONMENT_PATH",
      "ONLY_CMAKE_FIND_ROOT_PATH"
    ],
    "kwargs": {
      "DOC": "*",
      "HINTS": "*",
      "NAMES": "*",
      "PATHS": "*",
      "PATH_SUFFIXES": "*"
    }
  },
  "find_library": {
    "flags": [
      "CMAKE_FIND_ROOT_PATH_BOTH",
      "NO_CMAKE_ENVIRONMENT_PATH",
      "NO_CMAKE_FIND_ROOT_PATH",
      "NO_CMAKE_PATH",
      "NO_CMKE_SYSTEM_PATH",
      "NO_DEFAULT_PATH",
      "NO_SYSTEM_ENVIRONMENT_PATH",
      "ONLY_CMAKE_FIND_ROOT_PATH"
    ],
    "kwargs": {
      "DOC": "*",
      "HINTS": "*",
      "NAMES": "*",
      "PATHS": "*",
      "PATH_SUFFIXES": "*"
    }
  },
  "find_package": {
    "pargs": "*",
    "flags": [
      "EXACT",
      "MODULE",
      "REQUIRED",
      "NO_POLICY_SCOPE",
      "QUIET"
    ],
    "kwargs": {
      "COMPONENTS": "*",
      "OPTIONAL_COMPONENTS": "*"
    }
  },
  "find_path": {
    "flags": [
      "CMAKE_FIND_ROOT_PATH_BOTH",
      "NO_CMAKE_ENVIRONMENT_PATH",
      "NO_CMAKE_FIND_ROOT_PATH",
      "NO_CMAKE_PATH",
      "NO_CMKE_SYSTEM_PATH",
      "NO_DEFAULT_PATH",
      "NO_SYSTEM_ENVIRONMENT_PATH",
      "ONLY_CMAKE_FIND_ROOT_PATH"
    ],
    "kwargs": {
      "DOC": "*",
      "HINTS": "*",
      "NAMES": "*",
      "PATHS": "*",
      "PATH_SUFFIXES": "*"
    }
  },
  "find_program": {
    "flags": [
      "CMAKE_FIND_ROOT_PATH_BOTH",
      "NO_CMAKE_ENVIRONMENT_PATH",
      "NO_CMAKE_FIND_ROOT_PATH",
      "NO_CMAKE_PATH",
      "NO_CMAKE_SYSTEM_PATH",
      "NO_DEFAULT_PATH",
      "NO_SYSTEM_ENVIRONMENT_PATH",
      "ONLY_CMAKE_FIND_ROOT_PATH"
    ],
    "kwargs": {
      "DOC": "*",
      "HINTS": "*",
      "NAMES": "*",
      "PATHS": "*",
      "PATH_SUFFIXES": "*"
    }
  },
  "get_directory_property": {
    "kwargs": {
      "DIRECTORY": "*"
    }
  },
  "get_property": {
    "flags": [
      "BRIEF_DOCS",
      "DEFINED",
      "FULL_DOCS",
      "GLOBAL",
      "SET",
      "VARIABLE"
    ],
    "kwargs": {
      "CACHE": "*",
      "DIRECTORY": "*",
      "PROPERTY": "*",
      "SOURCE": "*",
      "TARGET": "*",
      "TEST": "*"
    }
  },
  "include": {
    "flags": [
      "NO_POLICY_SCOPE",
      "OPTIONAL"
    ],
    "kwargs": {
      "RESULT_VARIABLE": "*"
    }
  },
  "include_directories": {
    "flags": [
      "AFTER",
      "BEFORE",
      "SYSTEM"
    ],
    "kwargs": {}
  },
  "mark_as_advanced": {
    "flags": [
      "CLEAR",
      "FORCE"
    ],
    "kwargs": {}
  },
  "message": {
    "kwargs": {
      "AUTHOR_WARNING": "*",
      "DEPRECATION": "*",
      "FATAL_ERROR": "*",
      "SEND_ERROR": "*",
      "STATUS": "*",
      "WARNING": "*"
    }
  },
  "project": {
    "kwargs": {
      "DESCRIPTION": 1,
      "HOMEPAGE_URL": 1,
      "LANGUAGES": "*",
      "VERSION": "*"
    }
  },
  "set_directory_properties": {
    "kwargs": {
      "PROPERTIES": "*"
    }
  },
  "set_property": {
    "flags": [
      "APPEND",
      "APPEND_STRING",
      "GLOBAL"
    ],
    "kwargs": {
      "CACHE": "*",
      "DIRECTORY": "*",
      "PROPERTY": "*",
      "SOURCE": "*",
      "TARGET": "*",
      "TEST": "*"
    }
  },
  "set_tests_properties": {
    "kwargs": {
      "PROPERTIES": "*"
    }
  },
  "string": {
    "flags": [
      "@ONLY",
      "ESCAPE_QUOTES",
      "REVERSE",
      "UTC"
    ],
    "kwargs": {
      "ALPHABET": "*",
      "ASCII": "*",
      "COMPARE": "*",
      "CONCAT": "*",
      "CONFIGURE": "*",
      "FIND": "*",
      "LENGTH": "*",
      "MAKE_C_IDENTIFIER": "*",
      "MD5": "*",
      "RANDOM": "*",
      "RANDOM_SEED": "*",
      "REGEX": "*",
      "REPLACE": "*",
      "SHA1": "*",
      "SHA256": "*",
      "SHA384": "*",
      "SHA512": "*",
      "STRIP": "*",
      "SUBSTRING": "*",
      "TIMESTAMP": "*",
      "TOLOWER": "*",
      "TOUPPER": "*"
    }
  },
  "try_compile": {
    "kwargs": {
      "CMAKE_FLAGS": "*",
      "COMPILE_DEFINITIONS": "*",
      "COPY_FILE": "*",
      "LINK_LIBRARIES": "*",
      "OUTPUT_VARIABLE": "*",
      "RESULT_VAR": "*"
    }
  },
  "target_compile_options": {
    "kwargs": {
      "PRIVATE": "+",
      "PUBLIC": "+",
      "INTERFACE": "+"
    }
  },
  "target_include_directories": {
    "kwargs": {
      "PRIVATE": "+",
      "PUBLIC": "+",
      "INTERFACE": "+"
    }
  },
  "target_link_libraries": {
    "kwargs": {
      "PRIVATE": "+",
      "PUBLIC": "+",
      "INTERFACE": "+"
    }
  },
  "try_run": {
    "kwargs": {
      "ARGS": "*",
      "CMAKE_FLAGS": "*",
      "COMPILE_DEFINITIONS": "*",
      "COMPILE_OUTPUT_VARIABLE": "*",
      "OUTPUT_VARIABLE": "*",
      "RUN_OUTPUT_VARIABLE": "*"
    }
  }
}

GENERATED_FROM_MODULES = {
  "add_command": {
    "pargs": {
      "nargs": 1
    }
  },
  "add_compiler_export_flags": {
    "pargs": {
      "nargs": 0
    }
  },
  "add_feature_info": {
    "pargs": {
      "nargs": 3
    }
  },
  "add_file_dependencies": {
    "pargs": {
      "nargs": 1
    }
  },
  "add_flex_bison_dependency": {
    "pargs": {
      "nargs": 2
    }
  },
  "add_jar": {
    "kwargs": {
      "ENTRY_POINT": 1,
      "INCLUDE_JARS": "+",
      "MANIFEST": 1,
      "OUTPUT_DIR": 1,
      "OUTPUT_NAME": 1,
      "SOURCES": "+",
      "VERSION": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "adjust_cmake_system_variables": {
    "pargs": {
      "nargs": 1
    }
  },
  "android_add_test_data": {
    "kwargs": {
      "DEVICE_OBJECT_STORE": 1,
      "DEVICE_TEST_DIR": 1,
      "FILES": "+",
      "FILES_DEST": 1,
      "LIBS": "+",
      "LIBS_DEST": 1,
      "NO_LINK_REGEX": "+"
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "bison_target": {
    "kwargs": {
      "COMPILE_FLAGS": 1,
      "DEFINES_FILE": 1,
      "REPORT_FILE": 1,
      "VERBOSE": "+"
    },
    "pargs": {

      "nargs": "3+"
    }
  },
  "bison_target_option_defines": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "BISON_TARGET_option_defines"
  },
  "bison_target_option_extraopts": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "BISON_TARGET_option_extraopts"
  },
  "bison_target_option_report_file": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "BISON_TARGET_option_report_file"
  },
  "bison_target_option_verbose": {
    "pargs": {
      "nargs": 3
    },
    "spelling": "BISON_TARGET_option_verbose"
  },
  "check_c_compiler_flag": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_c_source_compiles": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_c_source_runs": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_compiler_flag_common_patterns": {
    "pargs": {
      "nargs": 1
    }
  },
  "check_cxx_accepts_flag": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_cxx_compiler_flag": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_cxx_source_compiles": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_cxx_source_runs": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_cxx_symbol_exists": {
    "pargs": {
      "nargs": 3
    }
  },
  "check_fortran_compiler_flag": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "CHECK_Fortran_COMPILER_FLAG"
  },
  "check_fortran_function_exists": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_fortran_libraries": {
    "pargs": {
      "nargs": 6
    },
    "spelling": "Check_Fortran_Libraries"
  },
  "check_fortran_source_compiles": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "CHECK_Fortran_SOURCE_COMPILES"
  },
  "check_function_exists": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_include_file": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_include_file_cxx": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_include_files": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_ipo_supported": {
    "kwargs": {
      "LANGUAGES": "+",
      "OUTPUT": 1,
      "RESULT": 1
    },
    "pargs": {

      "nargs": "*"
    }
  },
  "check_language": {
    "pargs": {
      "nargs": 1
    }
  },
  "check_lapack_libraries": {
    "pargs": {
      "nargs": 7
    },
    "spelling": "Check_Lapack_Libraries"
  },
  "check_library_exists": {
    "pargs": {
      "nargs": 4
    }
  },
  "check_prototype_definition": {
    "pargs": {
      "nargs": 5
    }
  },
  "check_required_var": {
    "pargs": {
      "nargs": 1
    }
  },
  "check_struct_has_member": {
    "pargs": {
      "nargs": 4
    }
  },
  "check_symbol_exists": {
    "pargs": {
      "nargs": 3
    }
  },
  "check_type_size": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_variable_exists": {
    "pargs": {
      "nargs": 2
    }
  },
  "check_version": {
    "pargs": {
      "nargs": 2
    }
  },
  "clear_bundle_keys": {
    "pargs": {
      "nargs": 1
    }
  },
  "cmake_add_fortran_subdirectory": {
    "kwargs": {
      "ARCHIVE_DIR": 1,
      "CMAKE_COMMAND_LINE": "+",
      "LIBRARIES": "+",
      "LINK_LIBRARIES": "+",
      "PROJECT": 1,
      "RUNTIME_DIR": 1
    },
    "pargs": {
      "flags": [
        "NO_EXTERNAL_INSTALL"
      ],
      "nargs": "1+"
    }
  },
  "cmake_dependent_option": {
    "pargs": {
      "nargs": 5
    }
  },
  "cmake_determine_compile_features": {
    "pargs": {
      "nargs": 1
    }
  },
  "cmake_determine_compiler_abi": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_determine_compiler_id": {
    "pargs": {
      "nargs": 3
    }
  },
  "cmake_determine_compiler_id_build": {
    "pargs": {
      "nargs": 4
    }
  },
  "cmake_determine_compiler_id_check": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_determine_compiler_id_match_vendor": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_determine_compiler_id_vendor": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_determine_compiler_id_write": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_determine_msvc_showincludes_prefix": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_diagnose_unsupported_clang": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_expand_imported_targets": {
    "kwargs": {
      "CONFIGURATION": 1,
      "LIBRARIES": "+"
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "cmake_export_build_settings": {
    "pargs": {
      "nargs": 1
    }
  },
  "cmake_find_frameworks": {
    "pargs": {
      "nargs": 1
    }
  },
  "cmake_force_c_compiler": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_force_cxx_compiler": {
    "pargs": {
      "nargs": 2
    }
  },
  "cmake_force_fortran_compiler": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "CMAKE_FORCE_Fortran_COMPILER"
  },
  "cmake_import_build_settings": {
    "pargs": {
      "nargs": 1
    }
  },
  "cmake_parse_implicit_link_info": {
    "pargs": {
      "nargs": 6
    }
  },
  "cmake_pop_check_state": {
    "pargs": {
      "nargs": 0
    }
  },
  "cmake_print_properties": {
    "kwargs": {
      "CACHE_ENTRIES": "+",
      "DIRECTORIES": "+",
      "PROPERTIES": "+",
      "SOURCES": "+",
      "TARGETS": "+",
      "TESTS": "+"
    },
    "pargs": {

      "nargs": "*"
    }
  },
  "cmake_print_variables": {
    "pargs": {
      "nargs": 0
    }
  },
  "cmake_push_check_state": {
    "pargs": {
      "nargs": 0
    }
  },
  "cmake_reset_check_state": {
    "pargs": {
      "nargs": 0
    }
  },
  "compiler_id_detection": {
    "kwargs": {
      "PREFIX": 1
    },
    "pargs": {
      "flags": [
        "ID_STRING",
        "VERSION_STRINGS",
        "ID_DEFINE",
        "PLATFORM_DEFAULT_COMPILER"
      ],
      "nargs": "2+"
    }
  },
  "configure_package_config_file": {
    "kwargs": {
      "INSTALL_DESTINATION": 1,
      "INSTALL_PREFIX": 1,
      "PATH_VARS": "+"
    },
    "pargs": {
      "flags": [
        "NO_SET_AND_CHECK_MACRO",
        "NO_CHECK_REQUIRED_COMPONENTS_MACRO"
      ],
      "nargs": "2+"
    }
  },
  "copy_and_fixup_bundle": {
    "pargs": {
      "nargs": 4
    }
  },
  "copy_resolved_framework_into_bundle": {
    "pargs": {
      "nargs": 2
    }
  },
  "copy_resolved_item_into_bundle": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_add_component": {
    "kwargs": {
      "ARCHIVE_FILE": 1,
      "DEPENDS": "+",
      "DESCRIPTION": 1,
      "DISPLAY_NAME": 1,
      "GROUP": 1,
      "INSTALL_TYPES": "+",
      "PLIST": 1
    },
    "pargs": {
      "flags": [
        "HIDDEN",
        "REQUIRED",
        "DISABLED",
        "DOWNLOADED"
      ],
      "nargs": "1+"
    }
  },
  "cpack_add_component_group": {
    "kwargs": {
      "DESCRIPTION": 1,
      "DISPLAY_NAME": 1,
      "PARENT_GROUP": 1
    },
    "pargs": {
      "flags": [
        "EXPANDED",
        "BOLD_TITLE"
      ],
      "nargs": "1+"
    }
  },
  "cpack_add_install_type": {
    "kwargs": {
      "DISPLAY_NAME": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "cpack_append_list_variable_set_command": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_append_option_set_command": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_append_string_variable_set_command": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_append_variable_set_command": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_check_file_exists": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_configure_downloads": {
    "kwargs": {
      "UPLOAD_DIRECTORY": 1
    },
    "pargs": {
      "flags": [
        "ALL",
        "ADD_REMOVE",
        "NO_ADD_REMOVE"
      ],
      "nargs": "1+"
    }
  },
  "cpack_deb_prepare_package_vars": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_deb_variable_fallback": {
    "pargs": {
      "nargs": 1
    }
  },
  "cpack_encode_variables": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_ifw_add_package_resources": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_ifw_add_repository": {
    "kwargs": {
      "DISPLAY_NAME": 1,
      "PASSWORD": 1,
      "URL": 1,
      "USERNAME": 1
    },
    "pargs": {
      "flags": [
        "DISABLED"
      ],
      "nargs": "1+"
    }
  },
  "cpack_ifw_configure_component": {
    "kwargs": {
      "AUTO_DEPEND_ON": "+",
      "CHECKABLE": 1,
      "DEFAULT": 1,
      "DEPENDENCIES": "+",
      "DEPENDS": "+",
      "DESCRIPTION": "+",
      "DISPLAY_NAME": "+",
      "LICENSES": "+",
      "NAME": 1,
      "PRIORITY": 1,
      "RELEASE_DATE": 1,
      "REPLACES": "+",
      "SCRIPT": 1,
      "SORTING_PRIORITY": 1,
      "TRANSLATIONS": "+",
      "UPDATE_TEXT": 1,
      "USER_INTERFACES": "+",
      "VERSION": 1
    },
    "pargs": {
      "flags": [
        "COMMON",
        "ESSENTIAL",
        "VIRTUAL",
        "FORCED_INSTALLATION",
        "REQUIRES_ADMIN_RIGHTS"
      ],
      "nargs": "1+"
    }
  },
  "cpack_ifw_configure_component_group": {
    "kwargs": {
      "AUTO_DEPEND_ON": "+",
      "CHECKABLE": 1,
      "DEFAULT": 1,
      "DEPENDENCIES": "+",
      "DEPENDS": "+",
      "DESCRIPTION": "+",
      "DISPLAY_NAME": "+",
      "LICENSES": "+",
      "NAME": 1,
      "PRIORITY": 1,
      "RELEASE_DATE": 1,
      "REPLACES": "+",
      "SCRIPT": 1,
      "SORTING_PRIORITY": 1,
      "TRANSLATIONS": "+",
      "UPDATE_TEXT": 1,
      "USER_INTERFACES": "+",
      "VERSION": 1
    },
    "pargs": {
      "flags": [
        "VIRTUAL",
        "FORCED_INSTALLATION",
        "REQUIRES_ADMIN_RIGHTS"
      ],
      "nargs": "1+"
    }
  },
  "cpack_ifw_configure_file": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_ifw_update_repository": {
    "kwargs": {
      "DISPLAY_NAME": 1,
      "NEW_URL": 1,
      "OLD_URL": 1,
      "PASSWORD": 1,
      "URL": 1,
      "USERNAME": 1
    },
    "pargs": {
      "flags": [
        "ADD",
        "REMOVE",
        "REPLACE",
        "DISABLED"
      ],
      "nargs": "1+"
    }
  },
  "cpack_optional_append": {
    "pargs": {
      "nargs": 3
    }
  },
  "cpack_rpm_debugsymbol_check": {
    "pargs": {
      "nargs": 2
    }
  },
  "cpack_rpm_generate_package": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_rpm_prepare_content_list": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_rpm_prepare_install_files": {
    "pargs": {
      "nargs": 4
    }
  },
  "cpack_rpm_prepare_relocation_paths": {
    "pargs": {
      "nargs": 0
    }
  },
  "cpack_rpm_symlink_add_for_relocation_script": {
    "pargs": {
      "nargs": 5
    }
  },
  "cpack_rpm_symlink_create_relocation_script": {
    "pargs": {
      "nargs": 1
    }
  },
  "cpack_rpm_symlink_get_relocation_prefixes": {
    "pargs": {
      "nargs": 3
    }
  },
  "cpack_rpm_variable_fallback": {
    "pargs": {
      "nargs": 1
    }
  },
  "cpack_set_if_not_set": {
    "pargs": {
      "nargs": 2
    }
  },
  "create_javadoc": {
    "pargs": {
      "nargs": 1
    }
  },
  "create_javah": {
    "kwargs": {
      "CLASSES": "+",
      "CLASSPATH": "+",
      "DEPENDS": "+",
      "GENERATED_FILES": 1,
      "OUTPUT_DIR": 1,
      "OUTPUT_NAME": 1,
      "TARGET": 1
    },
    "pargs": {

      "nargs": "*"
    }
  },
  "crt_version": {
    "pargs": {
      "nargs": 2
    }
  },
  "csharp_get_dependentupon_name": {
    "pargs": {
      "nargs": 2
    }
  },
  "csharp_get_filename_key_base": {
    "pargs": {
      "nargs": 2
    }
  },
  "csharp_get_filename_keys": {
    "pargs": {
      "nargs": 1
    }
  },
  "csharp_set_designer_cs_properties": {
    "pargs": {
      "nargs": 0
    }
  },
  "csharp_set_windows_forms_properties": {
    "pargs": {
      "nargs": 0
    }
  },
  "csharp_set_xaml_cs_properties": {
    "pargs": {
      "nargs": 0
    }
  },
  "ctest_coverage_collect_gcov": {
    "kwargs": {
      "BUILD": 1,
      "GCOV_COMMAND": 1,
      "GCOV_OPTIONS": "+",
      "SOURCE": 1,
      "TARBALL": 1
    },
    "pargs": {
      "flags": [
        "QUIET",
        "GLOB",
        "DELETE"
      ],
      "nargs": "*"
    }
  },
  "cuda_add_cublas_to_target": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_add_cuda_include_once": {
    "pargs": {
      "nargs": 0
    }
  },
  "cuda_add_cufft_to_target": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_add_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_add_library": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_build_clean_target": {
    "pargs": {
      "nargs": 0
    }
  },
  "cuda_build_shared_library": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_compile": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_compile_base": {
    "pargs": {
      "nargs": 3
    }
  },
  "cuda_compile_cubin": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_compile_fatbin": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_compile_ptx": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_compute_build_path": {
    "pargs": {
      "nargs": 2
    }
  },
  "cuda_compute_separable_compilation_object_file_name": {
    "pargs": {
      "nargs": 3
    }
  },
  "cuda_find_helper_file": {
    "pargs": {
      "nargs": 2
    }
  },
  "cuda_find_host_program": {
    "pargs": {
      "nargs": 0
    }
  },
  "cuda_find_library_local_first": {
    "pargs": {
      "nargs": 3
    }
  },
  "cuda_find_library_local_first_with_path_ext": {
    "pargs": {
      "nargs": 4
    }
  },
  "cuda_get_sources_and_options": {
    "pargs": {
      "nargs": 3
    }
  },
  "cuda_include_directories": {
    "pargs": {
      "nargs": 0
    }
  },
  "cuda_include_nvcc_dependencies": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_link_separable_compilation_objects": {
    "pargs": {
      "nargs": 4
    }
  },
  "cuda_parse_nvcc_options": {
    "pargs": {
      "nargs": 1
    }
  },
  "cuda_unset_include_and_libraries": {
    "pargs": {
      "nargs": 0
    }
  },
  "cuda_wrap_srcs": {
    "pargs": {
      "nargs": 3
    }
  },
  "cxxtest_add_test": {
    "pargs": {
      "nargs": 2
    }
  },
  "dbg_msg": {
    "pargs": {
      "nargs": 1
    }
  },
  "dbg_msg_v": {
    "pargs": {
      "nargs": 1
    }
  },
  "determinevsservicepack": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "DetermineVSServicePack"
  },
  "doxygen_add_docs": {
    "kwargs": {
      "COMMENT": 1,
      "WORKING_DIRECTORY": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "doxygen_list_to_quoted_strings": {
    "pargs": {
      "nargs": 1
    }
  },
  "doxygen_quote_value": {
    "pargs": {
      "nargs": 1
    }
  },
  "dump_file": {
    "pargs": {
      "nargs": 1
    }
  },
  "ecos_add_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "ecos_add_include_directories": {
    "pargs": {
      "nargs": 0
    }
  },
  "ecos_add_target_lib": {
    "pargs": {
      "nargs": 0
    }
  },
  "ecos_adjust_directory": {
    "pargs": {
      "nargs": 1
    }
  },
  "ecos_use_arm_elf_tools": {
    "pargs": {
      "nargs": 0
    }
  },
  "ecos_use_i386_elf_tools": {
    "pargs": {
      "nargs": 0
    }
  },
  "ecos_use_ppc_eabi_tools": {
    "pargs": {
      "nargs": 0
    }
  },
  "enable_language": {
    "pargs": {
      "nargs": 0
    }
  },
  "export_jars": {
    "kwargs": {
      "FILE": 1,
      "NAMESPACE": 1,
      "TARGETS": "+"
    },
    "pargs": {

      "nargs": "*"
    }
  },
  "externaldata_add_target": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "ExternalData_add_target"
  },
  "externaldata_add_test": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "ExternalData_add_test"
  },
  "externaldata_expand_arguments": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "ExternalData_expand_arguments"
  },
  "extract_matlab_versions_from_registry_brute_force": {
    "pargs": {
      "nargs": 1
    }
  },
  "extract_so_info": {
    "pargs": {
      "nargs": 3
    }
  },
  "feature_summary": {
    "kwargs": {
      "DESCRIPTION": 1,
      "FILENAME": 1,
      "VAR": 1,
      "WHAT": "+"
    },
    "pargs": {
      "flags": [
        "APPEND",
        "INCLUDE_QUIET_PACKAGES",
        "FATAL_ON_MISSING_REQUIRED_PACKAGES",
        "QUIET_ON_EMPTY",
        "DEFAULT_DESCRIPTION"
      ],
      "nargs": "*"
    }
  },
  "find_cuda_helper_libs": {
    "pargs": {
      "nargs": 1
    }
  },
  "find_dependency": {
    "pargs": {
      "nargs": 1
    }
  },
  "find_imagemagick_api": {
    "pargs": {
      "nargs": 2
    }
  },
  "find_imagemagick_exe": {
    "pargs": {
      "nargs": 1
    }
  },
  "find_jar": {
    "pargs": {
      "nargs": 1
    }
  },
  "find_library_local_first": {
    "pargs": {
      "nargs": 3
    }
  },
  "find_package_handle_standard_args": {
    "kwargs": {
      "FAIL_MESSAGE": 1,
      "FOUND_VAR": 1,
      "REQUIRED_VARS": "+",
      "VERSION_VAR": 1
    },
    "pargs": {
      "flags": [
        "CONFIG_MODE",
        "HANDLE_COMPONENTS"
      ],
      "nargs": "2+"
    }
  },
  "find_package_message": {
    "pargs": {
      "nargs": 3
    }
  },
  "fixup_bundle": {
    "kwargs": {
      "IGNORE_ITEM": "+"
    },
    "pargs": {

      "nargs": "3+"
    }
  },
  "fixup_bundle_item": {
    "pargs": {
      "nargs": 3
    }
  },
  "fixup_qt4_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "flex_target": {
    "kwargs": {
      "COMPILE_FLAGS": 1,
      "DEFINES_FILE": 1
    },
    "pargs": {

      "nargs": "3+"
    }
  },
  "fortrancinterface_header": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "FortranCInterface_HEADER"
  },
  "fortrancinterface_verify": {
    "pargs": {
      "nargs": 0
    },
    "spelling": "FortranCInterface_VERIFY"
  },
  "from_hex": {
    "pargs": {
      "nargs": 2
    }
  },
  "generate_export_header": {
    "pargs": {
      "nargs": 1
    }
  },
  "get_bundle_all_executables": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_bundle_and_executable": {
    "pargs": {
      "nargs": 4
    }
  },
  "get_bundle_keys": {
    "kwargs": {
      "IGNORE_ITEM": "+"
    },
    "pargs": {

      "nargs": "4+"
    }
  },
  "get_bundle_main_executable": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_component_package_name": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_dotapp_dir": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_item_key": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_item_rpaths": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_prerequisites": {
    "pargs": {
      "nargs": 6
    }
  },
  "get_unix_permissions_octal_notation": {
    "pargs": {
      "nargs": 2
    }
  },
  "get_vs_version_string": {
    "pargs": {
      "nargs": 2
    }
  },
  "getdefaultwindowsprefixbase": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "GetDefaultWindowsPrefixBase"
  },
  "gettext_create_translations": {
    "pargs": {
      "nargs": 2
    }
  },
  "gettext_process_po_files": {
    "kwargs": {
      "INSTALL_DESTINATION": 1,
      "PO_FILES": "+"
    },
    "pargs": {
      "flags": [
        "ALL"
      ],
      "nargs": "1+"
    }
  },
  "gettext_process_pot_file": {
    "kwargs": {
      "INSTALL_DESTINATION": 1,
      "LANGUAGES": "+"
    },
    "pargs": {
      "flags": [
        "ALL"
      ],
      "nargs": "1+"
    }
  },
  "gnuinstalldirs_get_absolute_install_dir": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "GNUInstallDirs_get_absolute_install_dir"
  },
  "gp_append_unique": {
    "pargs": {
      "nargs": 2
    }
  },
  "gp_file_type": {
    "pargs": {
      "nargs": 3
    }
  },
  "gp_item_default_embedded_path": {
    "pargs": {
      "nargs": 2
    }
  },
  "gp_resolve_item": {
    "pargs": {
      "nargs": 5
    }
  },
  "gp_resolved_file_type": {
    "pargs": {
      "nargs": 5
    }
  },
  "gtest_add_tests": {
    "kwargs": {
      "EXTRA_ARGS": "+",
      "SOURCES": "+",
      "TARGET": 1,
      "TEST_LIST": 1,
      "TEST_PREFIX": 1,
      "TEST_SUFFIX": 1,
      "WORKING_DIRECTORY": 1
    },
    "pargs": {
      "flags": [
        "SKIP_DEPENDENCY"
      ],
      "nargs": "*"
    }
  },
  "gtest_discover_tests": {
    "kwargs": {
      "EXTRA_ARGS": "+",
      "PROPERTIES": "+",
      "TEST_LIST": 1,
      "TEST_PREFIX": 1,
      "TEST_SUFFIX": 1,
      "TIMEOUT": 1,
      "WORKING_DIRECTORY": 1
    },
    "pargs": {
      "flags": [
        "NO_PRETTY_TYPES",
        "NO_PRETTY_VALUES"
      ],
      "nargs": "1+"
    }
  },
  "hg_wc_info": {
    "pargs": {
      "nargs": 2
    }
  },
  "install_jar": {
    "kwargs": {
      "COMPONENT": 1,
      "DESTINATION": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "install_jar_exports": {
    "kwargs": {
      "COMPONENT": 1,
      "DESTINATION": 1,
      "FILE": 1,
      "NAMESPACE": 1,
      "TARGETS": "+"
    },
    "pargs": {

      "nargs": "*"
    }
  },
  "install_jni_symlink": {
    "kwargs": {
      "COMPONENT": 1,
      "DESTINATION": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "install_qt4_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "install_qt4_plugin": {
    "pargs": {
      "nargs": 4
    }
  },
  "install_qt4_plugin_path": {
    "pargs": {
      "nargs": 4
    }
  },
  "ios_install_combined": {
    "pargs": {
      "nargs": 2
    }
  },
  "is_file_executable": {
    "pargs": {
      "nargs": 2
    }
  },
  "java_append_library_directories": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_dcop_skels": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_dcop_stubs": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_kcfg_files": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_kdeinit_executable": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_kpart": {
    "pargs": {
      "nargs": 2
    }
  },
  "kde3_add_moc_files": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_add_ui_files": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_automoc": {
    "pargs": {
      "nargs": 0
    }
  },
  "kde3_create_final_file": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_install_icons": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_install_libtool_file": {
    "pargs": {
      "nargs": 1
    }
  },
  "kde3_print_results": {
    "pargs": {
      "nargs": 0
    }
  },
  "link_resolved_item_into_bundle": {
    "pargs": {
      "nargs": 2
    }
  },
  "list_prerequisites": {
    "pargs": {
      "nargs": 1
    }
  },
  "list_prerequisites_by_glob": {
    "pargs": {
      "nargs": 2
    }
  },
  "macro_add_file_dependencies": {
    "pargs": {
      "nargs": 1
    }
  },
  "matlab_add_mex": {
    "kwargs": {
      "DOCUMENTATION": 1,
      "LINK_TO": "+",
      "NAME": 1,
      "OUTPUT_NAME": 1,
      "SRC": "+"
    },
    "pargs": {
      "flags": [
        "EXECUTABLE",
        "MODULE",
        "SHARED"
      ],
      "nargs": "*"
    }
  },
  "matlab_add_unit_test": {
    "kwargs": {
      "NO_UNITTEST_FRAMEWORK": "+",
      "_MATLAB_UNITTEST_PREFIX": 1
    },
    "pargs": {
      "flags": [
        "0"
      ],
      "nargs": "*"
    }
  },
  "matlab_extract_all_installed_versions_from_registry": {
    "pargs": {
      "nargs": 2
    }
  },
  "matlab_get_all_valid_matlab_roots_from_registry": {
    "pargs": {
      "nargs": 2
    }
  },
  "matlab_get_mex_suffix": {
    "pargs": {
      "nargs": 2
    }
  },
  "matlab_get_release_name_from_version": {
    "pargs": {
      "nargs": 2
    }
  },
  "matlab_get_supported_releases": {
    "pargs": {
      "nargs": 1
    }
  },
  "matlab_get_supported_versions": {
    "pargs": {
      "nargs": 1
    }
  },
  "matlab_get_version_from_matlab_run": {
    "pargs": {
      "nargs": 2
    }
  },
  "matlab_get_version_from_release_name": {
    "pargs": {
      "nargs": 2
    }
  },
  "mpi_search_mpi_prefix_folder": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "MPI_search_mpi_prefix_folder"
  },
  "msg": {
    "pargs": {
      "nargs": 1
    }
  },
  "osg_find_library": {
    "pargs": {
      "nargs": 2
    }
  },
  "osg_find_path": {
    "pargs": {
      "nargs": 2
    }
  },
  "osg_mark_as_advanced": {
    "pargs": {
      "nargs": 1
    }
  },
  "perl_adjust_darwin_lib_variable": {
    "pargs": {
      "nargs": 1
    }
  },
  "pkg_check_modules": {
    "pargs": {
      "nargs": 2
    }
  },
  "pkg_get_variable": {
    "pargs": {
      "nargs": 3
    }
  },
  "pkg_search_module": {
    "pargs": {
      "nargs": 2
    }
  },
  "pkgconfig": {
    "pargs": {
      "nargs": 5
    }
  },
  "print_disabled_features": {
    "pargs": {
      "nargs": 0
    }
  },
  "print_enabled_features": {
    "pargs": {
      "nargs": 0
    }
  },
  "printtestcompilerstatus": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "PrintTestCompilerStatus"
  },
  "processorcount": {
    "pargs": {
      "nargs": 1
    },
    "spelling": "ProcessorCount"
  },
  "protobuf_generate_cpp": {
    "kwargs": {
      "DESCRIPTORS": 1,
      "EXPORT_MACRO": 1
    },
    "pargs": {

      "nargs": "2+"
    }
  },
  "protobuf_generate_python": {
    "pargs": {
      "nargs": 1
    }
  },
  "python_add_module": {
    "pargs": {
      "nargs": 1
    }
  },
  "python_write_modules_header": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_add_dbus_adaptor": {
    "pargs": {
      "nargs": 4
    }
  },
  "qt4_add_dbus_interface": {
    "pargs": {
      "nargs": 3
    }
  },
  "qt4_add_dbus_interfaces": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_add_resources": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_add_translation": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_automoc": {
    "pargs": {
      "nargs": 0
    }
  },
  "qt4_create_moc_command": {
    "pargs": {
      "nargs": 5
    }
  },
  "qt4_create_translation": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_extract_options": {
    "pargs": {
      "nargs": 3
    }
  },
  "qt4_generate_dbus_interface": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_generate_moc": {
    "pargs": {
      "nargs": 2
    }
  },
  "qt4_get_moc_flags": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_make_output_file": {
    "pargs": {
      "nargs": 4
    }
  },
  "qt4_use_modules": {
    "pargs": {
      "nargs": 2
    }
  },
  "qt4_wrap_cpp": {
    "pargs": {
      "nargs": 1
    }
  },
  "qt4_wrap_ui": {
    "pargs": {
      "nargs": 1
    }
  },
  "resolve_qt4_paths": {
    "pargs": {
      "nargs": 1
    }
  },
  "rti_message_quietly": {
    "pargs": {
      "nargs": 3
    }
  },
  "select_library_configurations": {
    "pargs": {
      "nargs": 1
    }
  },
  "set_bundle_key_values": {
    "pargs": {
      "nargs": 6
    }
  },
  "set_compile_flags_var": {
    "pargs": {
      "nargs": 1
    }
  },
  "set_feature_info": {
    "pargs": {
      "nargs": 0
    }
  },
  "set_if_not_set": {
    "pargs": {
      "nargs": 2
    }
  },
  "set_if_set": {
    "pargs": {
      "nargs": 2
    }
  },
  "set_if_set_and_not_set": {
    "pargs": {
      "nargs": 2
    }
  },
  "set_link_flags_var": {
    "pargs": {
      "nargs": 1
    }
  },
  "set_package_info": {
    "pargs": {
      "nargs": 2
    }
  },
  "set_package_properties": {
    "kwargs": {
      "DESCRIPTION": 1,
      "PURPOSE": 1,
      "TYPE": 1,
      "URL": 1
    },
    "pargs": {

      "nargs": "2+"
    }
  },
  "source_files": {
    "pargs": {
      "nargs": 0
    }
  },
  "squish_add_test": {
    "pargs": {
      "nargs": 0
    }
  },
  "squish_v3_add_test": {
    "pargs": {
      "nargs": 5
    }
  },
  "squish_v4_add_test": {
    "kwargs": {
      "AUT": 1,
      "POST_COMMAND": 1,
      "PRE_COMMAND": 1,
      "SETTINGSGROUP": 1,
      "SUITE": 1,
      "TEST": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "subversion_wc_info": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "Subversion_WC_INFO"
  },
  "subversion_wc_log": {
    "pargs": {
      "nargs": 2
    },
    "spelling": "Subversion_WC_LOG"
  },
  "swig_add_library": {
    "kwargs": {
      "LANGUAGE": 1,
      "SOURCES": "+",
      "TYPE": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "swig_add_module": {
    "pargs": {
      "nargs": 2
    }
  },
  "swig_add_source_to_module": {
    "pargs": {
      "nargs": 3
    }
  },
  "swig_get_extra_output_files": {
    "pargs": {
      "nargs": 4
    }
  },
  "swig_link_libraries": {
    "pargs": {
      "nargs": 1
    }
  },
  "swig_module_initialize": {
    "pargs": {
      "nargs": 2
    }
  },
  "test_big_endian": {
    "pargs": {
      "nargs": 1
    }
  },
  "verify_app": {
    "kwargs": {
      "IGNORE_ITEM": "+"
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "verify_bundle_prerequisites": {
    "kwargs": {
      "IGNORE_ITEM": "+"
    },
    "pargs": {

      "nargs": "3+"
    }
  },
  "verify_bundle_symlinks": {
    "pargs": {
      "nargs": 3
    }
  },
  "write_basic_config_version_file": {
    "kwargs": {
      "COMPATIBILITY": 1,
      "VERSION": 1
    },
    "pargs": {

      "nargs": "1+"
    }
  },
  "write_basic_package_version_file": {
    "pargs": {
      "nargs": 0
    },
    "kwargs": {
      "COMPATABILITY": 1,
      "VERSION": 1
    }
  },
  "write_compiler_detection_header": {
    "kwargs": {
      "COMPILERS": "+",
      "EPILOG": 1,
      "FEATURES": "+",
      "OUTPUT_DIR": 1,
      "OUTPUT_FILES_VAR": 1,
      "PROLOG": 1,
      "VERSION": 1
    },
    "pargs": {
      "flags": [
        "ALLOW_UNKNOWN_COMPILERS",
        "ALLOW_UNKNOWN_COMPILER_VERSIONS"
      ],
      "nargs": "4+"
    }
  },
  "write_qt4_conf": {
    "pargs": {
      "nargs": 2
    }
  },
  "wx_clear_all_dbg_libs": {
    "pargs": {
      "nargs": 0
    }
  },
  "wx_clear_all_libs": {
    "pargs": {
      "nargs": 1
    }
  },
  "wx_clear_all_rel_libs": {
    "pargs": {
      "nargs": 0
    }
  },
  "wx_clear_lib": {
    "pargs": {
      "nargs": 1
    }
  },
  "wx_config_select_get_default": {
    "pargs": {
      "nargs": 0
    }
  },
  "wx_config_select_query_bool": {
    "pargs": {
      "nargs": 2
    }
  },
  "wx_config_select_set_options": {
    "pargs": {
      "nargs": 0
    }
  },
  "wx_find_libs": {
    "pargs": {
      "nargs": 3
    }
  },
  "wx_get_dependencies_from_xml": {
    "pargs": {
      "nargs": 5
    }
  },
  "wx_get_name_components": {
    "pargs": {
      "nargs": 4
    }
  },
  "wx_set_libraries": {
    "pargs": {
      "nargs": 2
    }
  },
  "wx_split_arguments_on": {
    "pargs": {
      "nargs": 3
    }
  },
  "wxwidgets_add_resources": {
    "pargs": {
      "nargs": 1
    }
  },
  "xctest_add_bundle": {
    "pargs": {
      "nargs": 2
    }
  },
  "xctest_add_test": {
    "pargs": {
      "nargs": 2
    }
  }
}
