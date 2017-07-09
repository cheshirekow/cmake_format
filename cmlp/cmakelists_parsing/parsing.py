from collections import namedtuple
import re

from . import list_utils

QuotedString = namedtuple('QuotedString', 'contents comments')
_Arg = namedtuple('Arg', 'contents comments')
_Command = namedtuple('Command', 'name body comment')
BlankLine = namedtuple('BlankLine', '')

class File(list):
    """Top node of the syntax tree for a CMakeLists file."""

    def __str__(self):
        '''
        Returns the pretty-print string for tree
        with indentation given by the string tab.
        '''
        return '\n'.join(compose_lines(self)) + '\n'

    def __repr__(self):
        return 'File(' + repr(list(self)) + ')'

class Comment(str):
    def __repr__(self):
        return 'Comment(' + str(self) + ')'

def Arg(contents, comments=None):
    return _Arg(contents, comments or [])

def Command(name, body, comment=None):
    return _Command(name, body, comment)

class CMakeParseError(Exception):
    pass

def prettify(s):
    """
    Returns the pretty-print of the contents of a CMakeLists file.
    """
    return str(parse(s))

def parse(s, path='<string>'):
    '''
    Parses a string s in CMakeLists format whose
    contents are assumed to have come from the
    file at the given path.
    '''
    nums_toks = tokenize(s)
    nums_items = list(parse_file(nums_toks))
    nums_items = attach_comments_to_commands(nums_items)
    items = [item for _, item in nums_items]
    return File(items)

def strip_blanks(tree):
    return File([x for x in tree if not isinstance(x, BlankLine)])

def compose_lines(tree, max_width=79):
    """
    Yields pretty-printed lines of a CMakeLists file.
    """
    tab = '\t'
    level = 0
    for item in tree:
        if isinstance(item, (Comment, str)):
            yield level * tab + item
        elif isinstance(item, BlankLine):
            yield ''
        elif isinstance(item, _Command):
            name = item.name.lower()
            if name in ('endfunction', 'endmacro', 'endif', 'else'):
                level -= 1
            for i, line in enumerate(command_to_lines(item)):
                offset = 1 if i > 0 else 0
                line2 = (level + offset) * tab + line
                if len(line2) <= max_width:
                    yield line2
                else:
                    command_to_lines
                    # Line is too long. Try again.
                    for _, (ty, contents) in tokenize(line):
                        yield (level + offset) * tab + contents

            if name in ('function', 'macro', 'if', 'else'):
                level += 1

# FIXME: Make this split into more lines if the result would be too wide.
def command_to_lines(cmd, sep):
    final_paren = ')' if cmd.body and cmd.body[-1].comments else ')'
    comment_part = '  ' + cmd.comment if cmd.comment else ''
    result = cmd.name + '(' + sep.join(map(arg_to_str, cmd.body)) + final_paren + comment_part
    return [l.strip() for l in result.splitlines()]

def arg_to_str(arg):
    comment_part = '  ' + '\n'.join(arg.comments) + '\n' if arg.comments else ''
    return arg.contents + comment_part

def parse_file(toks):
    '''
    Yields line number ranges and top-level elements of the syntax tree for
    a CMakeLists file, given a generator of tokens from the file.

    toks must really be a generator, not a list, for this to work.
    '''
    prev_type = 'newline'
    for line_num, (typ, tok_contents) in toks:
        if typ == 'comment':
            yield ([line_num], Comment(tok_contents))
        elif typ == 'newline' and prev_type == 'newline':
            yield ([line_num], BlankLine())
        elif typ == 'word':
            line_nums, cmd = parse_command(line_num, tok_contents, toks)
            yield (line_nums, cmd)
        prev_type = typ

def attach_comments_to_commands(nodes):
    return list_utils.merge_pairs(nodes, command_then_comment, attach_comment_to_command)

def command_then_comment(a, b):
    line_nums_a, thing_a = a
    line_nums_b, thing_b = b
    return (isinstance(thing_a, _Command) and
            isinstance(thing_b, Comment) and
            set(line_nums_a).intersection(line_nums_b))

def attach_comment_to_command(lnums_command, lnums_comment):
    command_lines, command = lnums_command
    _, comment = lnums_comment
    return command_lines, Command(command.name, command.body[:], comment)

def parse_command(start_line_num, command_name, toks):
    cmd = Command(name=command_name, body=[], comment=None)
    open_paren_count = 0
    expect('left paren', toks)
    for line_num, (typ, tok_contents) in toks:
        if typ == 'right paren':
            if open_paren_count == 0:
                line_nums = range(start_line_num, line_num + 1)
                return line_nums, cmd
            else:
                open_paren_count -= 1
                cmd.body.append(Arg(tok_contents, []))
        elif typ == 'left paren':
            open_paren_count += 1
            cmd.body.append(Arg(tok_contents, []))
            #raise ValueError('Unexpected left paren at line %s' % line_num)
        elif typ in ('word', 'string'):
            cmd.body.append(Arg(tok_contents, []))
        elif typ == 'comment':
            c = tok_contents
            if cmd.body:
                cmd.body[-1].comments.append(c)
            else:
                cmd.comments.append(c)
    msg = 'File ended while processing command "%s" started at line %s' % (
        command_name, start_line_num)
    raise CMakeParseError(msg)

def expect(expected_type, toks):
    line_num, (typ, tok_contents) = toks.next()
    if typ != expected_type:
        msg = 'Expected a %s, but got "%s" at line %s' % (
            expected_type, tok_contents, line_num)
        raise CMakeParseError(msg)

# http://stackoverflow.com/questions/691148/pythonic-way-to-implement-a-tokenizer
string_regex = re.compile(r'".*[^\\]?"', re.DOTALL)
scanner = re.Scanner([
    (r'#[^\n]*',            lambda scanner, token: ("comment", token)),
    (r'".*[^\\]?"',         lambda scanner, token: ("string", token)),
    (r"\(",                 lambda scanner, token: ("left paren", token)),
    (r"\)",                 lambda scanner, token: ("right paren", token)),
    (r'[^ \t\r\n()#"]+',    lambda scanner, token: ("word", token)),
    (r'\n',                 lambda scanner, token: ("newline", token)),
    (r"\s+",                None), # skip other whitespace
], re.DOTALL)

def tokenize(s):
    """
    Yields pairs of the form (line_num, (token_type, token_contents))
    given a string containing the contents of a CMakeLists file.
    """

    toks, remainder = scanner.scan(s)
    if remainder != '':
        msg = 'Unrecognized tokens at line %s: %s' % (-1, remainder)
        raise ValueError(msg)
    line_num = 1
    for tok_type, tok_contents in toks:
        yield line_num, (tok_type, tok_contents.strip())
        line_num += tok_contents.count('\n')
