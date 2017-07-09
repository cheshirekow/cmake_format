"""Parse cmake listfiles and format them nicely."""

import argparse
import collections
import os
import re
import shutil
import sys
import tempfile
import textwrap
import yaml

# Make sure we use our patched version of cmakelists_parsing. If we are calling
# this file as a script then get this directory on the path before importing
# cmakelists_parsing. Otherwise use a package relative import.
if __name__ == '__main__':
    THIS_DIR = os.path.realpath(os.path.dirname(__file__))
    sys.path.insert(0, THIS_DIR)
    from cmlp.cmakelists_parsing import parsing as cmparse
else:
    from .cmlp.cmakelists_parsing import parsing as cmparse

class AttrDict(dict):
    """Access elements of a dictionary as attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def build_attr_dict_r(regular_dict):
    """Recursively construct an AttrDict from a regular one."""
    attr_dict = AttrDict()
    for key, value in regular_dict.iteritems():
        if isinstance(value, dict):
            attr_dict[key] = build_attr_dict_r(value)
        else:
            attr_dict[key] = value
    return attr_dict

SCOPE_INCREASE = ['if', 'foreach', 'while', 'function', 'macro']
SCOPE_DEDENT = ['else']
SCOPE_DECREASE = ['endif', 'endforeach', 'endwhile', 'endfunction', 'endmacro']

NOTE_REGEX = re.compile(r'^[A-Z_]+\([^)]+\):.*')

# TODO(josh): some KWARGS don't take parameters, and these we want to treat
# differently.
KWARG_REGEX = re.compile(r'[A-Z0-9_]+')

DEFAULT_CONFIG = build_attr_dict_r(dict(
    line_width=80,
    tab_size=2,
    # TODO(josh): make this conditioned on certain commands / kwargs
    # because things like execute_process(COMMAND...) are less readable
    # formatted as a single list. In fact... special case COMMAND to break on
    # flags the way we do kwargs.
    max_subargs_per_line=3,
    additional_flags=dict(),
    additional_kwargs=dict(),
))

# TODO(josh): Can we do better with a full function spec like this?
CMAKE_FN_SPEC = {
    'add_custom_command' : {
        'kwargs' : {
            'OUTPUT' : '+',
            'COMMAND' : '+',
            'MAIN_DEPENDENCY' : 1,
            'DEPENDS' : '*',
            'IMPLICIT_DEPENDS' : '*',
            'WORKING_DIRECTORY' : 1,
            'COMMENT' : '*',
            'VERBATIM' : 0,
            'APPEND' : 0
        }
    }
}

# Maps command name to flag args, which are like kwargs but don't take',
# subargument lists
FLAG_MAP = {
    'add_custom_command':
        ['APPEND',
         'VERBATIM'],
    'add_custom_target':
        ['ALL',
         'VERBATIM'],
    'add_executable':
        ['WIN32',
         'MACOSX_BUNDLE',
         'EXCLUDE_FROM_ALL'],
    'add_library':
        ['STATIC',
         'SHARED',
         'MODULE',
         'EXCLUDE_FROM_ALL'],
    'cmake_minimum_required':
        ['FATAL_ERROR'],
    'configure_file':
        ['COPYONLY',
         'ESCAPE_QUOTES',
         '@ONLY'],
    'define_property':
        ['GLOBAL',
         'DIRECTORY',
         'TARGET',
         'SOURCE',
         'TEST',
         'VARIABLE',
         'CACHED_VARIABLE',
         'INHERITED'],
    'enable_language':
        ['OPTIONAL'],
    'execute_process':
        ['OUTPUT_QUIET',
         'ERROR_QUIET',
         'OUTPUT_STRIP_TRAILING_WHITESPACE',
         'ERROR_STRIP_TRAILING_WHITESPACE'],
    'file':
        ['HEX',
         'NEWLINE_CONSUME',
         'NO_HEX_CONVERSION',
         'FOLLOW_SYMLINKS',
         'SHOW_PROGRESS',
         'UTC',
         'GENERATE'],
    'find_file':
        ['NO_DEFAULT_PATH',
         'NO_CMAKE_ENVIRONMENT_PATH',
         'NO_CMAKE_PATH',
         'NO_SYSTEM_ENVIRONMENT_PATH',
         'NO_CMKE_SYSTEM_PATH',
         'CMAKE_FIND_ROOT_PATH_BOTH',
         'ONLY_CMAKE_FIND_ROOT_PATH',
         'NO_CMAKE_FIND_ROOT_PATH'],
    'find_library':
        ['NO_DEFAULT_PATH',
         'NO_CMAKE_ENVIRONMENT_PATH',
         'NO_CMAKE_PATH',
         'NO_SYSTEM_ENVIRONMENT_PATH',
         'NO_CMKE_SYSTEM_PATH',
         'CMAKE_FIND_ROOT_PATH_BOTH',
         'ONLY_CMAKE_FIND_ROOT_PATH',
         'NO_CMAKE_FIND_ROOT_PATH'],
    'find_package':
        ['EXACT',
         'QUIET',
         'MODULE'
         'REQUIRED'
         'NO_POLICY_SCOPE'],
    'find_path':
        ['NO_DEFAULT_PATH',
         'NO_CMAKE_ENVIRONMENT_PATH',
         'NO_CMAKE_PATH',
         'NO_SYSTEM_ENVIRONMENT_PATH',
         'NO_CMKE_SYSTEM_PATH',
         'CMAKE_FIND_ROOT_PATH_BOTH',
         'ONLY_CMAKE_FIND_ROOT_PATH',
         'NO_CMAKE_FIND_ROOT_PATH'],
    'find_program':
        ['NO_DEFAULT_PATH',
         'NO_CMAKE_ENVIRONMENT_PATH',
         'NO_CMAKE_PATH',
         'NO_SYSTEM_ENVIRONMENT_PATH',
         'NO_CMKE_SYSTEM_PATH',
         'CMAKE_FIND_ROOT_PATH_BOTH',
         'ONLY_CMAKE_FIND_ROOT_PATH',
         'NO_CMAKE_FIND_ROOT_PATH'],
    'get_property':
        ['GLOBAL',
         'VARIABLE',
         'SET',
         'DEFINED',
         'BRIEF_DOCS',
         'FULL_DOCS'],
    'include_directories':
        ['AFTER',
         'BEFORE',
         'SYSTEM'],
    'include':
        ['OPTIONAL',
         'NO_POLICY_SCOPE'],
    'install':
        ['OPTIONAL',
         'NAMELINK_ONLY',
         'NAMELINK_SKIP',
         'USE_SOURCE_PERMISSIONS'],
    'mark_as_advanced':
        ['CLEAR',
         'FORCE'],
    'set_property':
        ['GLOBAL',
         'APPEND',
         'APPEND_STRING'],
    'set':
        ['FORCE',
         'PARENT_SCOPE'],
    'string':
        ['REVERSE',
         'UTC',
         '@ONLY',
         'ESCAPE_QUOTES'],
}

# Maps command names to lists of kwargs
KWARG_MAP = collections.defaultdict(list, {
    'add_custom_command':
        ['OUTPUT',
         'COMMAND',
         'MAIN_DEPENDENCY',
         'DEPENDS',
         'IMPLICIT_DEPENDS',
         'WORKING_DIRECTORY',
         'COMMENT'],
    'add_custom_target':
        ['COMMAND',
         'DEPENDS',
         'WORKING_DIRECTORY',
         'COMMENT',
         'SOURCES'],
    'add_test':
        ['NAME',
         'COMMAND',
         'CONFIGURATIONS',
         'WORKING_DIRECTORY'],
    'cmake_host_system_information':
        ['RESULT',
         'QUERY'],
    'cmake_minimum_required_version':
        ['VERSION'],
    'configure_file':
        ['NEWLINE_STYLE'],
    'define_property':
        ['PROPERTY',
         'BRIEF_DOCS',
         'FULL_DOCS'],
    'execute_process':
        ['COMMAND',
         'WORKING_DIRECTORY',
         'TIMEOUT',
         'RESULT_VARIABLE',
         'OUTPUT_VARIABLE',
         'ERROR_VARIABLE',
         'INPUT_FILE',
         'OUTPUT_FILE',
         'ERROR_FILE'],
    'file':
        ['WRITE',
         'APPEND',
         'READ',
         'LIMIT',
         'OFFSET',
         'MD5',
         'SHA1',
         'SHA256',
         'SHA384',
         'SHA512',
         'STRINGS',
         'LIMIT_COUNT',
         'LIMIT_INPUT',
         'LIMIT_OUTPUT',
         'LENGTH_MINIMUM',
         'LENGTH_MAXIMUM',
         'REGEX',
         'GLOB',
         'RELATIVE',
         'GLOB_RECURSE',
         'RENAME',
         'REMOVE',
         'REMOVE_RECURSE',
         'MAKE_DIRECTORY',
         'RELATIVE_PATH',
         'TO_CMAKE_PATH',
         'TO_NATIVE_PATH',
         'DOWNLOAD',
         'INACTIVITY_TIMEOUT',
         'TIMEOUT',
         'STATUS',
         'LOG',
         'EXPECTED_HASH',
         'EXPECTED_MD5',
         'TLS_VERIFY',
         'TLS_CAINFO',
         'UPLOAD',
         'TIMESTAMP',
         'OUTPUT'
         'INPUT'
         'CONTENT'
         'CONDITION'],
    'find_file':
        ['NAMES',
         'HINTS',
         'PATHS',
         'PATH_SUFFIXES',
         'DOC'],
    'find_library':
        ['NAMES',
         'HINTS',
         'PATHS',
         'PATH_SUFFIXES',
         'DOC'],
    'find_package':
        ['COMPONENTS',
         'OPTIONAL_COMPONENTS'],
    'find_path':
        ['NAMES',
         'HINTS',
         'PATHS',
         'PATH_SUFFIXES',
         'DOC'],
    'find_program':
        ['NAMES',
         'HINTS',
         'PATHS',
         'PATH_SUFFIXES',
         'DOC'],
    'get_directory_property':
        ['DIRECTORY'],
    'get_property':
        ['DIRECTORY',
         'TARGET',
         'SOURCE',
         'TEST',
         'CACHE',
         'PROPERTY'],
    'include':
        ['RESULT_VARIABLE'],
    'install':
        ['TARGETS',
         'EXPORT',
         'ARCHIVE',
         'LIBRARY',
         'RUNTIME',
         'FRAMEWORK',
         'BUNDLE',
         'PRIVATE_HEADER',
         'PUBLIC_HEADER',
         'RESOURCE',
         'INCLUDES'
         'PERMISSIONS',
         'CONFIGURATIONS',
         'COMPONENT',
         'FILES',
         'PROGRAMS',
         'RENAME',
         'DIRECTORY',
         'FILE_PERMISSIONS',
         'DIRECTORY_PERMISSIONS',
         'FILES_MATCHING'],
    'list':
        ['LENGTH',
         'GET',
         'APPEND',
         'FIND',
         'INSERT',
         'REMOVE_ITEM',
         'REMOVE_AT',
         'REMOVE_DUPLICATES',
         'REVERSE',
         'SORT'],
    'message':
        ['STATUS',
         'WARNING',
         'AUTHOR_WARNING',
         'SEND_ERROR',
         'FATAL_ERROR',
         'DEPRECATION'],
    'project':
        ['LANGUAGES',
         'VERSION'],
    'set':
        ['CACHE'],
    'set_directory_properties':
        ['PROPERTIES'],
    'set_property':
        ['DIRECTORY',
         'TARGET',
         'SOURCE',
         'TEST',
         'CACHE',
         'PROPERTY'],
    'set_target_properties':
        ['PROPERTIES'],
    'set_tests_properties':
        ['PROPERTIES'],
    'string':
        ['REGEX',
         'REPLACE',
         'CONCAT',
         'MD5',
         'SHA1',
         'SHA256',
         'SHA384',
         'SHA512',
         'COMPARE',
         'ASCII',
         'CONFIGURE',
         'TOUPPER',
         'TOLOWER',
         'LENGTH',
         'SUBSTRING',
         'STRIP',
         'RANDOM',
         'LENGTH',
         'ALPHABET',
         'RANDOM_SEED',
         'FIND',
         'TIMESTAMP',
         'MAKE_C_IDENTIFIER'],
    'try_compile':
        ['RESULT_VAR',
         'CMAKE_FLAGS',
         'OUTPUT_VARIABLE',
         'COMPILE_DEFINITIONS',
         'LINK_LIBRARIES',
         'COPY_FILE'],
    'try_run':
        ['CMAKE_FLAGS',
         'COMPILE_DEFINITIONS',
         'COMPILE_OUTPUT_VARIABLE',
         'RUN_OUTPUT_VARIABLE',
         'OUTPUT_VARIABLE',
         'ARGS']
})


def indent_list(indent_str, lines):
    """Return a list of lines where indent_str is prepended to everything in
       lines."""
    return [indent_str + line for line in lines]


def format_comment_block(config, line_width, comment_lines):
    """Reflow a comment block into the given line_width. Return a list of
       lines."""
    stripped_lines = [line[1:].strip() for line in comment_lines]

    paragraph_lines = list()
    paragraphs = list()
    # A new "paragraph" starts at a paragraph boundary (double newline), or at
    # the start of a TODO(...): or NOTE(...):
    for line in stripped_lines:
        if NOTE_REGEX.match(line):
            if paragraph_lines:
                paragraphs.append(' '.join(paragraph_lines))
            paragraph_lines = [line]
        elif line:
            paragraph_lines.append(line)
        else:
            if paragraph_lines:
                paragraphs.append(' '.join(paragraph_lines))
            paragraphs.append('')
            paragraph_lines = list()
    if paragraph_lines:
        paragraphs.append(' '.join(paragraph_lines))

    lines = []
    for paragraph_text in paragraphs:
        if not paragraph_text:
            lines.append('#')
            continue
        wrapper = textwrap.TextWrapper(width=line_width,
                                       expand_tabs=True,
                                       replace_whitespace=True,
                                       drop_whitespace=True,
                                       initial_indent='# ',
                                       subsequent_indent='# ')
        lines.extend(wrapper.wrap(paragraph_text))
    return lines


def is_flag(command_name, arg):
    """Return true if the given argument is a flag."""
    if command_name in FLAG_MAP:
        return arg.contents in FLAG_MAP[command_name]
    return False


def is_kwarg(command_name, arg):
    """Return true if the given argument is a kwarg."""
    if command_name in KWARG_MAP:
        return arg.contents in KWARG_MAP[command_name]
    return False


def split_args_by_kwargs(command_name, args):
    """Takes in a list of arguments and returns a list of lists. Each sublist
       is either a list of positional arguments, a list containg a kwarg
       followed by it's sub arguments, or a list containing a consecutive
       sequence of flags."""
    arg_split = [[]]
    for arg in args:
        if is_flag(command_name, arg):
            if len(arg_split[-1]) > 0:
                if not is_flag(command_name, arg_split[-1][-1]):
                    arg_split.append([])
        elif is_kwarg(command_name, arg):
            if len(arg_split[-1]) > 0:
                arg_split.append([])
        arg_split[-1].append(arg)

    return arg_split


def arg_exists_with_comment(args):
    """Return true if any arg in the arglist contains a comment."""
    for arg in args:
        if arg.comments:
            return True
    return False


def format_single_arg(config, line_width, arg):
    """Return a list of lines that reflow the single arg and all it's comments
       into a block with width at most line_width."""
    if arg.comments:
        comment_stream = ' '.join([comment[1:].strip()
                                   for comment in arg.comments])
        initial_indent = arg.contents + ' # '
        subsequent_indent = ' ' * len(arg.contents) + ' # '
        wrapper = textwrap.TextWrapper(width=line_width,
                                       expand_tabs=True,
                                       replace_whitespace=True,
                                       drop_whitespace=True,
                                       initial_indent=initial_indent,
                                       subsequent_indent=subsequent_indent)
        return wrapper.wrap(comment_stream)
    else:
        return [arg.contents]

def split_shell_command(args):
    """Given a list of arguments to a COMMAND, try to match flags and split
       args into groups based on the location of flags (-f or --foo)."""
    arglist = []
    for arg in args:
        if arg.contents.startswith('-'):
            arglist.append([arg])
        elif len(arglist) > 0:
            arglist[-1].append(arg)
        else:
            arglist.append([arg])
    return arglist

def format_shell_command(config, line_width, command_name, args):
    """Format arguments into a block with at most line_width chars."""

    if not arg_exists_with_comment(args):
        single_line = ' '.join([arg.contents for arg in args])
        if len(single_line) < line_width:
            return [single_line]

    lines = []
    arg_multilist = split_shell_command(args)

    # Look for strings of single arguments that can be joined together
    arg_multilist_filtered = []
    for arg_sublist in arg_multilist:
        if len(arg_sublist) == 1 and len(arg_multilist_filtered) > 0:
            arg_multilist_filtered[-1].append(arg_sublist[0])
        else:
            arg_multilist_filtered.append(arg_sublist)


    for arg_sublist in arg_multilist_filtered:
        sublist_lines = format_arglist(config, line_width, command_name,
                                       arg_sublist)
        lines.extend(sublist_lines)

    return lines


def format_arglist(config, line_width, command_name, args):
    """Given a list arguments containing at most one KWARG (in position [0]
       if it exists), format into a list of lines."""
    if len(args) < 1:
        return []

    if is_kwarg(command_name, args[0]):
        kwarg = args[0].contents

        if len(args) == 1:
            return [kwarg]

        # If the KWARG is 'COMMAND' then let's not put one entry per line,
        # but fit as many command args per line as possible.
        if kwarg == 'COMMAND':
            # Copy the config and override max subargs per line
            config = build_attr_dict_r(config)
            # pylint: disable=attribute-defined-outside-init
            config.max_subargs_per_line = 1e6

            aligned_indent_str = ' ' * (len(kwarg) + 1)
            tabbed_indent_str = ' ' * config.tab_size

            # Lines to append if we put them aligned with the end of the kwarg
            line_width_aligned = line_width - len(aligned_indent_str)
            lines_aligned = format_shell_command(config,
                                                 line_width_aligned,
                                                 args[1].contents, args[1:])

            # Lines to append if we put them on lines after the kwarg and
            # indented one block higher
            line_width_tabbed = line_width - len(tabbed_indent_str)
            lines_tabbed = format_shell_command(config,
                                                line_width_tabbed,
                                                args[1].contents, args[1:])

        else:
            aligned_indent_str = ' ' * (len(kwarg) + 1)
            tabbed_indent_str = ' ' * config.tab_size

            # Lines to append if we put them aligned with the end of the kwarg
            lines_aligned = format_arglist(config,
                                           line_width - len(aligned_indent_str),
                                           command_name, args[1:])

            # Lines to append if we put them on lines after the kwarg and
            # indented one block higher
            lines_tabbed = format_arglist(config,
                                          line_width - len(tabbed_indent_str),
                                          command_name, args[1:])

        # If aligned doesn't fit, then use tabbed
        if (get_block_width(lines_aligned)
                > line_width - len(aligned_indent_str)):
            return [kwarg] + indent_list(tabbed_indent_str, lines_tabbed)
        else:
            return ([kwarg + ' ' + lines_aligned[0]]
                    + indent_list(aligned_indent_str, lines_aligned[1:]))

    indent_str = ''
    lines = ['']

    # TODO(josh): if aligning after the KWARG exeeds line width, then move one
    # line below and align to the start + one indent.

    # if the there are "lots" of arguments in the list, put one per line,
    # but we can't reuse the logic below since we do want to append to the
    # first line.
    if len(args) > config.max_subargs_per_line:
        first_lines = format_single_arg(config, line_width - len(indent_str),
                                        args[0])
        if len(lines[-1]) > 0:
            lines[-1] += ' '
        lines[-1] += first_lines[0]
        for line in first_lines[1:]:
            lines.append(indent_str + line)
        for arg in args[1:]:
            for line in format_single_arg(config,
                                          line_width - len(indent_str), arg):
                lines.append(indent_str + line)
        return lines

    for arg in args:
        # Lines to add if we were to put the arg at the end of the current
        # line.
        lines_append = format_single_arg(config,
                                         line_width - len(lines[-1]) - 1, arg)

        # Lines to add if we are going to make a new line for this arg
        lines_new = format_single_arg(
            config, line_width - len(indent_str), arg)

        # If going to a new line greatly reduces the number of lines required
        # then choose that option over the latter.
        if (len(lines_append[0]) + len(lines[-1]) + 1 > line_width
                or 4 * len(lines_new) < len(lines_append)):
            for line in lines_new:
                lines.append(indent_str + line)
        else:
            arg_indent_str = ' ' * (len(lines[-1]) + 1)
            if len(lines[-1]) > 0:
                lines[-1] += ' '
            lines[-1] += lines_append[0]

            for line in lines_append[1:]:
                lines.append(arg_indent_str + line)

    return lines


def format_args(config, line_width, command_name, args):
    """Format arguments into a block with at most line_width chars."""

    # If there are no arguments that contain a comment, then attempt to
    # pack all of the arguments onto a single line
    if not arg_exists_with_comment(args):
        single_line = ' '.join([arg.contents for arg in args])
        if len(single_line) < line_width:
            return [single_line]

    lines = []
    arg_multilist = split_args_by_kwargs(command_name, args)

    # Look for strings of single arguments that can be joined together
    arg_multilist_filtered = []
    for arg_sublist in arg_multilist:

        max_subargs = config.max_subargs_per_line
        if (len(arg_sublist) == 1 and len(arg_multilist_filtered) > 0
                and len(arg_multilist_filtered[-1]) < max_subargs):
            arg_multilist_filtered[-1].append(arg_sublist[0])
        else:
            arg_multilist_filtered.append(arg_sublist)


    for arg_sublist in arg_multilist_filtered:
        sublist_lines = format_arglist(config, line_width, command_name,
                                       arg_sublist)
        lines.extend(sublist_lines)

    return lines


def get_block_width(lines):
    """Return the max width of any line within the list of lines."""
    return max(len(line) for line in lines)

def format_command(config, command, line_width):
    """Formats a cmake command call into a block with at most line_width chars.
       Returns a list of lines."""

    command_start = command.name + '('

    # If there are no args then return just the command
    if len(command.body) < 1:
        return [command_start + ')']
    else:
        # Format args into a block that is aligned with the end of the
        # parenthesis after the command name
        lines_a = format_args(config, line_width - len(command_start),
                              command.name, command.body)

        # Format args into a block that is aligned with the command start
        # plus one tab size
        lines_b = format_args(config,
                              line_width - config.tab_size,
                              command.name, command.body)

        # If the version aligned with the comand start + indent has *alot*
        # fewer lines than the version aligned with the command end, then
        # use this one. Also use it if the first option exceeds line width.
        if (len(lines_a) > 4 * len(lines_b)
                or get_block_width(lines_a) > line_width - len(command_start)):
            lines = [command_start]
            indent_str = ' ' * config.tab_size
            for line in lines_b:
                lines.append(indent_str + line)
            if len(lines[-1]) < line_width and not command.body[-1].comments:
                lines[-1] += ')'
            else:
                lines.append(indent_str[:-1] + ')')

        # Otherwise use the version that is alinged with the command ending
        else:
            lines = [command_start + lines_a[0]]
            indent_str = ' ' * len(command_start)
            for line in lines_a[1:]:
                lines.append(indent_str + line)
            if len(lines[-1]) < line_width and not command.body[-1].comments:
                lines[-1] += ')'
            else:
                lines.append(indent_str[:-1] + ')')

        # If the comman itself has a trailing line comment then attempt to
        # keep the comment attached to the command, but consider also moving
        # the comment to it's own line if that uses up a lot less lines.
        if command.comment:
            line_width_append = line_width - len(lines[-1]) - 1
            comment_lines_append = format_comment_block(config,
                                                        line_width_append,
                                                        [command.comment])

            comment_lines_extend = format_comment_block(config, line_width,
                                                        [command.comment])

            if len(comment_lines_append) < 4 * len(comment_lines_extend):
                append_indent = ' ' * (len(lines[-1]) + 1)
                lines[-1] += ' ' + comment_lines_append[0]
                lines.extend(indent_list(append_indent,
                                         comment_lines_append[1:]))
            else:
                lines.extend(comment_lines_extend)
    return lines


def write_indented(outfile, indent_str, lines):
    """Write lines to outfile prefixed with indent_str."""

    for line in lines:
        outfile.write(indent_str)
        outfile.write(line)
        outfile.write('\n')


class PrettyPrinter(object):
    """Manages state during processing of file lines. Accumulates newlines and
       comment lines so that they can be reflowed / reformatted as text."""

    def __init__(self, config, outfile):
        self.config = config
        self.outfile = outfile
        self.scope_depth = 0
        self.indent = config.tab_size
        self.line_width = config.line_width
        self.comment_parts = list()
        self.blank_parts = list()

    def flush_blanks(self):
        """Consume a string of blank lines and write out a single one."""

        if self.blank_parts:
            self.outfile.write('\n')
            self.blank_parts = list()

    def flush_comment(self):
        """Consume a string of comment lines, reflow, and write out."""

        if self.comment_parts:
            indent_str = ' ' * (self.config.tab_size * self.scope_depth)
            lines = format_comment_block(self.config,
                                         self.config.line_width
                                         - len(indent_str),
                                         self.comment_parts)
            write_indented(self.outfile, indent_str, lines)
            self.comment_parts = list()

    def consume_part(self, part):
        """Consume a single parsed object."""

        if isinstance(part, cmparse.BlankLine):
            self.flush_comment()
            self.blank_parts.append(part)
        elif isinstance(part, cmparse.Comment):
            self.flush_blanks()
            self.comment_parts.append(part)

        elif isinstance(part, cmparse._Command):  # pylint: disable=protected-access
            self.flush_comment()
            self.flush_blanks()
            command = part
            if command.name in SCOPE_DECREASE or command.name in SCOPE_DEDENT:
                self.scope_depth -= 1

            indent_str = ' ' * (self.config.tab_size * self.scope_depth)
            lines = format_command(self.config, command,
                                   self.config.line_width - len(indent_str))
            write_indented(self.outfile, indent_str, lines)

            if command.name in SCOPE_INCREASE or command.name in SCOPE_DEDENT:
                self.scope_depth += 1

        else:
            raise ValueError('Unrecognized parse type {}'.format(type(part)))

    def consume_parts(self, parsed_listfile):
        """Consume a list of parsed cmake objects."""

        for part in parsed_listfile:
            self.consume_part(part)
        self.flush_comment()
        self.flush_blanks()


def process_file(config, infile, outfile):
    """Iterates through lines in the file and watches for cmake_format on/off
       sentinels. Consumes lines for formatting when active, and passes through
       to the outfile when not."""
    pretty_printer = PrettyPrinter(config, outfile)

    active = True
    format_me = ''
    for line in iter(infile.readline, b''):
        if active:
            if line.find('cmake_format: off') != -1:
                parsed_listfile = cmparse.parse(format_me)
                pretty_printer.consume_parts(parsed_listfile)
                parsed_listfile = cmparse.parse(line)
                pretty_printer.consume_parts(parsed_listfile)
                format_me = ''
                active = False
            else:
                format_me += line
        else:

            if line.find('cmake_format: on') != -1:
                parsed_listfile = cmparse.parse(line)
                pretty_printer.consume_parts(parsed_listfile)
                active = True
                format_me = ''
            else:
                outfile.write(line)

    if format_me:
        parsed_listfile = cmparse.parse(format_me)
        pretty_printer.consume_parts(parsed_listfile)


def merge_config(merge_into, merge_from):
    """Recursively merge dictionary from-to."""

    for key, value in merge_into.iteritems():
        if key in merge_from:
            if isinstance(value, AttrDict):
                merge_config(value, merge_from[key])
            else:
                merge_into[key] = type(merge_into[key])(merge_from[key])

def main():
    """Parse arguments, open files, start work."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--in-place', action='store_true')
    parser.add_argument('-o', '--outfile-path', default='-',
                        help='Where to write the formatted file. '
                             'Default is stdout.')
    parser.add_argument('-c', '--config-file', help='path to yaml config')
    parser.add_argument('infilepaths', nargs='+')
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    if args.config_file:
        with open(args.config_file, 'r') as config_file:
            config_dict = yaml.load(config_file)
        merge_config(config, config_dict)

    FLAG_MAP.update(config_dict.get('additional_flags'))
    KWARG_MAP.update(config_dict.get('additional_kwargs'))

    for infile_path in args.infilepaths:
        if args.in_place:
            outfile = tempfile.NamedTemporaryFile(delete=False)
        else:
            if args.outfile_path == '-':
                outfile = sys.stdout
            else:
                outfile = open(args.outfile_path, 'w')

        parse_ok = True
        try:
            with open(infile_path, 'r') as infile:
                process_file(config, infile, outfile)
        except:
            parse_ok = False
            sys.stderr.write('While processing {}\n'.format(infile_path))
            raise
        finally:
            if args.in_place:
                outfile.close()
                if parse_ok:
                    shutil.move(outfile.name, infile_path)
            else:
                if args.outfile_path != '-':
                    outfile.close()

if __name__ == '__main__':
    main()
