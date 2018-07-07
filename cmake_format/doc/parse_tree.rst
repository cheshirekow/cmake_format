================
CMake Parse Tree
================

This document is intended to describe the high level organization of how
cmake listfiles are parsed and organized into an abstract syntax tree.

Digestion and formatting  of a listfile is done in four phases:

  * tokenization
  * parsing
  * layout tree construction
  * layout / reflow

---------
Tokenizer
---------

Listfiles are first digested into a sequence of tokens. The tokenizer is
implemented in `lexer.py` an defines the following types of tokens:

+------------------+---------------------------------------+-------------------+
| Token Type       | Description                           | Example           |
+------------------+---------------------------------------+-------------------+
| QUOTED_LITERAL   | A single or double quoted string,     | ``"foo"``         |
|                  | from the first quote to the first     | ``'bar'``         |
|                  | subsequent un-escaped quote           |                   |
+------------------+---------------------------------------+-------------------+
| BRACKET_ARGUMENT | A bracket-quoted argument of a        |``[=[hello foo]=]``|
|                  | cmake-statement                       |                   |
+------------------+---------------------------------------+-------------------+
| NUMBER           | Unquoted numeric literal              | ``1234``          |
+------------------+---------------------------------------+-------------------+
| LEFT_PAREN       | A left parenthesis                    | ``(``             |
+------------------+---------------------------------------+-------------------+
| RIGHT_PAREN      | A right parenthesis                   | ``)``             |
+------------------+---------------------------------------+-------------------+
| WORD             | An unquoted literal string which      | ``foo``           |
|                  | matches lexical rules such that it    | ``foo_bar``       |
|                  | could be a cmake entity name, such    |                   |
|                  | as the name of a function or variable |                   |
+------------------+---------------------------------------+-------------------+
| DEREF            | A variable dereference expression,    | ``${foo}``        |
|                  | from the dollar sign up to the outer  | ``${foo_${bar}}`` |
|                  | most right curly brace                |                   |
+------------------+---------------------------------------+-------------------+
| NEWLINE          | A single carriage return, newline or  |                   |
|                  | (carriage-return, newline) pair       |                   |
+------------------+---------------------------------------+-------------------+
| WHITESPACE       | A continuous sequence of space, tab   |                   |
|                  | or other ascii whitespace             |                   |
+------------------+---------------------------------------+-------------------+
| BRACKET_COMMENT  | A bracket-quoted comment string       |``#[=[hello]=]``   |
+------------------+---------------------------------------+-------------------+
| COMMENT          | A single line starting with a hash    |``# hello world``  |
+------------------+---------------------------------------+-------------------+
| UNQUOTED_LITERAL | A sequence of non-whitespace          | ``--verbose``     |
|                  | characters used as a cmake argument   |                   |
|                  | but not satisfying the requirements of|                   |
|                  | a cmake name                          |                   |
+------------------+---------------------------------------+-------------------+
| FORMAT_OFF       | A special comment disabling           | ``cmake-format:`` |
|                  | cmake-format temporarily              | `` off``          |
+------------------+---------------------------------------+-------------------+
| FORMAT_OFF       | A special comment re-enabling         | ``cmake-format:`` |
|                  |                                       | `` on``           |
+------------------+---------------------------------------+-------------------+

Each token covers a continuous sequence of characters of the input file.
Futhermore, the sequence of tokens digest from the file covers the entire range
of infile offsets. The ``Token`` object stores information about the input file
byte offset, line number, and column number of it's start location. Note that
for ``utf-8`` input where a character may be composed of more than one byte,
the ``(row, col)`` location is the location of the character while the
``offset`` is the index of the first byte of the character.

You can inspect the tokenization of a listfile by executing ``cmake-format``
with ``--dump lex``. For example::

    Token(type=WORD, content=u'cmake_minimum_required', line=1, col=0)
    Token(type=LEFT_PAREN, content=u'(', line=1, col=22)
    Token(type=WORD, content=u'VERSION', line=1, col=23)
    Token(type=WHITESPACE, content=u' ', line=1, col=30)
    Token(type=UNQUOTED_LITERAL, content=u'3.5', line=1, col=31)
    Token(type=RIGHT_PAREN, content=u')', line=1, col=34)
    Token(type=NEWLINE, content=u'\n', line=1, col=35)
    Token(type=WORD, content=u'project', line=2, col=0)
    Token(type=LEFT_PAREN, content=u'(', line=2, col=7)
    Token(type=WORD, content=u'demo', line=2, col=8)
    Token(type=RIGHT_PAREN, content=u')', line=2, col=12)
    Token(type=NEWLINE, content=u'\n', line=2, col=13)
    Token(type=WORD, content=u'if', line=3, col=0)
    Token(type=LEFT_PAREN, content=u'(', line=3, col=2)
    Token(type=WORD, content=u'FOO', line=3, col=3)
    Token(type=WHITESPACE, content=u' ', line=3, col=6)
    Token(type=WORD, content=u'AND', line=3, col=7)
    Token(type=WHITESPACE, content=u' ', line=3, col=10)
    Token(type=LEFT_PAREN, content=u'(', line=3, col=11)
    Token(type=WORD, content=u'BAR', line=3, col=12)
    Token(type=WHITESPACE, content=u' ', line=3, col=15)
    Token(type=WORD, content=u'OR', line=3, col=16)
    Token(type=WHITESPACE, content=u' ', line=3, col=18)
    Token(type=WORD, content=u'BAZ', line=3, col=19)
    Token(type=RIGHT_PAREN, content=u')', line=3, col=22)
    Token(type=RIGHT_PAREN, content=u')', line=3, col=23)
    Token(type=NEWLINE, content=u'\n', line=3, col=24)
    Token(type=WHITESPACE, content=u'  ', line=4, col=0)
    Token(type=WORD, content=u'add_library', line=4, col=2)
    Token(type=LEFT_PAREN, content=u'(', line=4, col=13)
    Token(type=WORD, content=u'hello', line=4, col=14)
    Token(type=WHITESPACE, content=u' ', line=4, col=19)
    Token(type=UNQUOTED_LITERAL, content=u'hello.cc', line=4, col=20)
    Token(type=RIGHT_PAREN, content=u')', line=4, col=28)
    Token(type=NEWLINE, content=u'\n', line=4, col=29)
    Token(type=WORD, content=u'endif', line=5, col=0)
    Token(type=LEFT_PAREN, content=u'(', line=5, col=5)
    Token(type=RIGHT_PAREN, content=u')', line=5, col=6)
    Token(type=NEWLINE, content=u'\n', line=5, col=7)

-------------------
Parser: Syntax Tree
-------------------

As of version ``0.4.0``, ``cmake-format`` parses the token stream in a single
pass. The state machine of the parser is maintained by the program stack
(i.e. the parse functions are called recursively) and each node type in the
tree has it's own parse function.

There are twelve types of nodes in the parse tree. They are described below
along with the list of possible child node types.


Node Types
==========

+--------------+---------------------------------------------+-----------------+
| Node Type    | Description                                 | Allowed Children|
+--------------+---------------------------------------------+-----------------+
| BODY         | A generic section of a cmake document. This | COMMENT         |
|              | node type is found at the root of the parse | STATEMENT       |
|              | tree and within conditional/flow control    | WHITESPACE      |
|              | statements                                  |                 |
|              |                                             |                 |
+--------------+---------------------------------------------+-----------------+
| WHITESPACE   | A consecutive sequence of whitespace tokens | (none)          |
|              | between any two other types of nodes.       |                 |
+--------------+---------------------------------------------+-----------------+
| COMMENT      | A sequence of one or more comment lines.    | (token)         |
|              | The node consistes of all consecutive       |                 |
|              | comment lines unbroken by additional        |                 |
|              | newlines or a single BRACKET_COMMENT token. |                 |
+--------------+---------------------------------------------+-----------------+
| STATEMENT    | A cmake statement (i.e. function call)      | ARGGROUP        |
|              |                                             | COMMENT         |
|              |                                             | FUNNAME         |
+--------------+---------------------------------------------+-----------------+
| FLOW_CONTROL | Two or more cmake statements and their      | STATEMENT       |
|              | nested bodies representing a flow control   | BODY            |
|              | construct (i.e. ``if`` or ``foreach``).     |                 |
+--------------+---------------------------------------------+-----------------+
| ARGGROUP     | A parenthetical grouping of zero or more    | ARGGROUP        |
|              | arguments.                                  | KWARGGROUP      |
|              |                                             | ARGUMENT        |
|              |                                             | COMMENT         |
|              |                                             | FLAG            |
+--------------+---------------------------------------------+-----------------+
| KWARGGROUP   | A KEYWORD group, starting with the keyword  | ARGGROUP        |
|              | and ending with the last argument associated| KWARGGROUP      |
|              | with that keyword                           | ARGUMENT        |
|              |                                             | COMMENT         |
|              |                                             | FLAG            |
+--------------+---------------------------------------------+-----------------+
| FUNNAME      | Consists of a single token containing the   | (none)          |
|              | name of the function/command in a statement |                 |
|              | with that keyword                           |                 |
+--------------+---------------------------------------------+-----------------+
| ARGUMENT     | Consists of a single token, containing the  | (token)         |
|              | literal argument of a statement, and        | COMMENT         |
|              | optionally a comment associated with it     |                 |
+--------------+---------------------------------------------+-----------------+
| KEYWORD      | Consists of a single token, containing the  | (token)         |
|              | literal keyword of a keyword group, and     | COMMENT         |
|              | optionally a comment associated with it     |                 |
+--------------+---------------------------------------------+-----------------+
| FLAG         | Consists of a single token, containing the  | (token)         |
|              | literal keyword of a statment flag, and     | COMMENT         |
|              | optionally a comment associated with it     |                 |
+--------------+---------------------------------------------+-----------------+
| ONOFFSWITCH  | Consists of a single token, containing the  | (none)          |
|              | sentinal comment line ``# cmake-format: on``|                 |
|              | or ``# cmake-format: off``.                 |                 |
+--------------+---------------------------------------------+-----------------+

You can inspect the parse tree of a listfile by ``cmake-format`` with
``--dump parse``. For example::

    └─ BODY: 1:0
        ├─ STATEMENT: 1:0
        │   ├─ FUNNAME: 1:0
        │   │   └─ Token(type=WORD, content=u'cmake_minimum_required', line=1, col=0)
        │   ├─ Token(type=LEFT_PAREN, content=u'(', line=1, col=22)
        │   ├─ ARGGROUP: 1:23
        │   │   └─ KWARGGROUP: 1:23
        │   │       ├─ KEYWORD: 1:23
        │   │       │   └─ Token(type=WORD, content=u'VERSION', line=1, col=23)
        │   │       ├─ Token(type=WHITESPACE, content=u' ', line=1, col=30)
        │   │       └─ ARGUMENT: 1:31
        │   │           └─ Token(type=UNQUOTED_LITERAL, content=u'3.5', line=1, col=31)
        │   └─ Token(type=RIGHT_PAREN, content=u')', line=1, col=34)
        ├─ WHITESPACE: 1:35
        │   └─ Token(type=NEWLINE, content=u'\n', line=1, col=35)
        ├─ STATEMENT: 2:0
        │   ├─ FUNNAME: 2:0
        │   │   └─ Token(type=WORD, content=u'project', line=2, col=0)
        │   ├─ Token(type=LEFT_PAREN, content=u'(', line=2, col=7)
        │   ├─ ARGGROUP: 2:8
        │   │   └─ ARGUMENT: 2:8
        │   │       └─ Token(type=WORD, content=u'demo', line=2, col=8)
        │   └─ Token(type=RIGHT_PAREN, content=u')', line=2, col=12)
        ├─ WHITESPACE: 2:13
        │   └─ Token(type=NEWLINE, content=u'\n', line=2, col=13)
        ├─ FLOW_CONTROL: 3:0
        │   ├─ STATEMENT: 3:0
        │   │   ├─ FUNNAME: 3:0
        │   │   │   └─ Token(type=WORD, content=u'if', line=3, col=0)
        │   │   ├─ Token(type=LEFT_PAREN, content=u'(', line=3, col=2)
        │   │   ├─ ARGGROUP: 3:3
        │   │   │   ├─ ARGUMENT: 3:3
        │   │   │   │   └─ Token(type=WORD, content=u'FOO', line=3, col=3)
        │   │   │   ├─ Token(type=WHITESPACE, content=u' ', line=3, col=6)
        │   │   │   └─ KWARGGROUP: 3:7
        │   │   │       ├─ KEYWORD: 3:7
        │   │   │       │   └─ Token(type=WORD, content=u'AND', line=3, col=7)
        │   │   │       ├─ Token(type=WHITESPACE, content=u' ', line=3, col=10)
        │   │   │       └─ ARGGROUP: 3:11
        │   │   │           ├─ Token(type=LEFT_PAREN, content=u'(', line=3, col=11)
        │   │   │           ├─ ARGUMENT: 3:12
        │   │   │           │   └─ Token(type=WORD, content=u'BAR', line=3, col=12)
        │   │   │           ├─ Token(type=WHITESPACE, content=u' ', line=3, col=15)
        │   │   │           ├─ KWARGGROUP: 3:16
        │   │   │           │   ├─ KEYWORD: 3:16
        │   │   │           │   │   └─ Token(type=WORD, content=u'OR', line=3, col=16)
        │   │   │           │   ├─ Token(type=WHITESPACE, content=u' ', line=3, col=18)
        │   │   │           │   └─ ARGUMENT: 3:19
        │   │   │           │       └─ Token(type=WORD, content=u'BAZ', line=3, col=19)
        │   │   │           └─ Token(type=RIGHT_PAREN, content=u')', line=3, col=22)
        │   │   └─ Token(type=RIGHT_PAREN, content=u')', line=3, col=23)
        │   ├─ BODY: 3:24
        │   │   ├─ WHITESPACE: 3:24
        │   │   │   ├─ Token(type=NEWLINE, content=u'\n', line=3, col=24)
        │   │   │   └─ Token(type=WHITESPACE, content=u'  ', line=4, col=0)
        │   │   ├─ STATEMENT: 4:2
        │   │   │   ├─ FUNNAME: 4:2
        │   │   │   │   └─ Token(type=WORD, content=u'add_library', line=4, col=2)
        │   │   │   ├─ Token(type=LEFT_PAREN, content=u'(', line=4, col=13)
        │   │   │   ├─ ARGGROUP: 4:14
        │   │   │   │   ├─ ARGUMENT: 4:14
        │   │   │   │   │   └─ Token(type=WORD, content=u'hello', line=4, col=14)
        │   │   │   │   ├─ Token(type=WHITESPACE, content=u' ', line=4, col=19)
        │   │   │   │   └─ ARGUMENT: 4:20
        │   │   │   │       └─ Token(type=UNQUOTED_LITERAL, content=u'hello.cc', line=4, col=20)
        │   │   │   └─ Token(type=RIGHT_PAREN, content=u')', line=4, col=28)
        │   │   └─ WHITESPACE: 4:29
        │   │       └─ Token(type=NEWLINE, content=u'\n', line=4, col=29)
        │   └─ STATEMENT: 5:0
        │       ├─ FUNNAME: 5:0
        │       │   └─ Token(type=WORD, content=u'endif', line=5, col=0)
        │       ├─ Token(type=LEFT_PAREN, content=u'(', line=5, col=5)
        │       ├─ ARGGROUP: 0:0
        │       └─ Token(type=RIGHT_PAREN, content=u')', line=5, col=6)
        └─ WHITESPACE: 5:7
            └─ Token(type=NEWLINE, content=u'\n', line=5, col=7)


----------------------
Formatter: Layout Tree
----------------------

As of version ``0.4.0``, ``cmake-format`` will create a tree structure parallel
to the parse tree and called the "layout tree". Each node in the layout tree
points to at most one node in the parse tree. The structure of the layout tree
is essentially the same as the parse tree with the following exceptions:

1. The primary argument group of a statement is expanded, so that the possible
   children of a ``STATEMENT`` layout node are: ``ARGGROUP``, ``ARGUMENT``,
   ``COMMENT``, ``FLAG``, ``FUNNAME``, ``KWARGROUP``.
2. ``WHITESPACE`` nodes containing less than two newlines are dropped, and not
   represented in the layout tree.

You can inspect the layout tree of a listfile by ``cmake-format`` with
``--dump layout``. For example::

    └─ BODY,HPACK(0) p(0,0) ce:35
        ├─ STATEMENT,HPACK(0) p(0,0) ce:35
        │   ├─ FUNNAME,HPACK(0) p(0,0) ce:22
        │   └─ KWARGGROUP,HPACK(0) p(0,23) ce:34
        │       ├─ KEYWORD,HPACK(0) p(0,23) ce:30
        │       └─ ARGUMENT,HPACK(0) p(0,31) ce:34
        ├─ STATEMENT,HPACK(0) p(1,0) ce:13
        │   ├─ FUNNAME,HPACK(0) p(1,0) ce:7
        │   └─ ARGUMENT,HPACK(0) p(1,8) ce:12
        └─ FLOW_CONTROL,HPACK(0) p(2,0) ce:29
            ├─ STATEMENT,HPACK(0) p(2,0) ce:24
            │   ├─ FUNNAME,HPACK(0) p(2,0) ce:2
            │   ├─ ARGUMENT,HPACK(0) p(2,3) ce:6
            │   └─ KWARGGROUP,HPACK(0) p(2,7) ce:23
            │       ├─ KEYWORD,HPACK(0) p(2,7) ce:10
            │       └─ ARGGROUP,HPACK(0) p(2,11) ce:23
            │           ├─ ARGUMENT,HPACK(0) p(2,12) ce:15
            │           └─ KWARGGROUP,HPACK(0) p(2,16) ce:22
            │               ├─ KEYWORD,HPACK(0) p(2,16) ce:18
            │               └─ ARGUMENT,HPACK(0) p(2,19) ce:22
            ├─ BODY,HPACK(0) p(3,2) ce:29
            │   └─ STATEMENT,HPACK(0) p(3,2) ce:29
            │       ├─ FUNNAME,HPACK(0) p(3,2) ce:13
            │       ├─ ARGUMENT,HPACK(0) p(3,14) ce:19
            │       └─ ARGUMENT,HPACK(0) p(3,20) ce:28
            └─ STATEMENT,HPACK(0) p(4,0) ce:7
                └─ FUNNAME,HPACK(0) p(4,0) ce:5

------------
Example file
------------

The example file used to create the tree dumps above is:::

    cmake_minimum_required(VERSION 3.5)
    project(demo)
    if(FOO AND (BAR OR BAZ))
      add_library(hello hello.cc)
    endif()
