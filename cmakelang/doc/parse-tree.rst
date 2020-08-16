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
implemented in `lex.py` an defines the following types of tokens:

+------------------+--------------------------------------+-------------------+
| Token Type       | Description                          | Example           |
+------------------+--------------------------------------+-------------------+
| QUOTED_LITERAL   | A single or double quoted string,    | ``"foo"``         |
|                  | from the first quote to the first    | ``'bar'``         |
|                  | subsequent un-escaped quote          |                   |
+------------------+--------------------------------------+-------------------+
| BRACKET_ARGUMENT | A bracket-quoted argument of a       |``[=[hello foo]=]``|
|                  | cmake-statement                      |                   |
+------------------+--------------------------------------+-------------------+
| NUMBER           | Unquoted numeric literal             | ``1234``          |
+------------------+--------------------------------------+-------------------+
| LEFT_PAREN       | A left parenthesis                   | ``(``             |
+------------------+--------------------------------------+-------------------+
| RIGHT_PAREN      | A right parenthesis                  | ``)``             |
+------------------+--------------------------------------+-------------------+
| WORD             | An unquoted literal string which     | ``foo``           |
|                  | matches lexical rules such that it   | ``foo_bar``       |
|                  | could be a cmake entity name, such   |                   |
|                  | as the name of a function or         |                   |
|                  | variable                             |                   |
+------------------+--------------------------------------+-------------------+
| DEREF            | A variable dereference expression,   | ``${foo}``        |
|                  | from the dollar sign up to the outer | ``${foo_${bar}}`` |
|                  | most right curly brace               |                   |
+------------------+--------------------------------------+-------------------+
| NEWLINE          | A single carriage return, newline or |                   |
|                  | (carriage-return, newline) pair      |                   |
+------------------+--------------------------------------+-------------------+
| WHITESPACE       | A continuous sequence of space, tab  |                   |
|                  | or other ascii whitespace            |                   |
+------------------+--------------------------------------+-------------------+
| BRACKET_COMMENT  | A bracket-quoted comment string      |``#[=[hello]=]``   |
+------------------+--------------------------------------+-------------------+
| COMMENT          | A single line starting with a hash   |``# hello world``  |
+------------------+--------------------------------------+-------------------+
| UNQUOTED_LITERAL | A sequence of non-whitespace         | ``--verbose``     |
|                  | characters used as a cmake argument  |                   |
|                  | but not satisfying the requirements  |                   |
|                  | of a cmake name                      |                   |
+------------------+--------------------------------------+-------------------+
| FORMAT_OFF       | A special comment disabling          | ``cmake-format:`` |
|                  | cmake-format temporarily             | `` off``          |
+------------------+--------------------------------------+-------------------+
| FORMAT_OFF       | A special comment re-enabling        | ``cmake-format:`` |
|                  |                                      | `` on``           |
+------------------+--------------------------------------+-------------------+

Each token covers a continuous sequence of characters of the input file.
Futhermore, the sequence of tokens digest from the file covers the entire range
of infile offsets. The ``Token`` object stores information about the input file
byte offset, line number, and column number of it's start location. Note that
for ``utf-8`` input where a character may be composed of more than one byte,
the ``(row, col)`` location is the location of the character while the
``offset`` is the index of the first byte of the character.

You can inspect the tokenization of a listfile by executing ``cmake-format``
with ``--dump lex``. For example:

.. dynamic: dump-example-lex-begin

.. code:: text

    Token(type=NEWLINE, content='\n', line=1, col=0)
    Token(type=WORD, content='cmake_minimum_required', line=2, col=0)
    Token(type=LEFT_PAREN, content='(', line=2, col=22)
    Token(type=WORD, content='VERSION', line=2, col=23)
    Token(type=WHITESPACE, content=' ', line=2, col=30)
    Token(type=UNQUOTED_LITERAL, content='3.5', line=2, col=31)
    Token(type=RIGHT_PAREN, content=')', line=2, col=34)
    Token(type=NEWLINE, content='\n', line=2, col=35)
    Token(type=WORD, content='project', line=3, col=0)
    Token(type=LEFT_PAREN, content='(', line=3, col=7)
    Token(type=WORD, content='demo', line=3, col=8)
    Token(type=RIGHT_PAREN, content=')', line=3, col=12)
    Token(type=NEWLINE, content='\n', line=3, col=13)
    Token(type=WORD, content='if', line=4, col=0)
    Token(type=LEFT_PAREN, content='(', line=4, col=2)
    Token(type=WORD, content='FOO', line=4, col=3)
    Token(type=WHITESPACE, content=' ', line=4, col=6)
    Token(type=WORD, content='AND', line=4, col=7)
    Token(type=WHITESPACE, content=' ', line=4, col=10)
    Token(type=LEFT_PAREN, content='(', line=4, col=11)
    Token(type=WORD, content='BAR', line=4, col=12)
    Token(type=WHITESPACE, content=' ', line=4, col=15)
    Token(type=WORD, content='OR', line=4, col=16)
    Token(type=WHITESPACE, content=' ', line=4, col=18)
    Token(type=WORD, content='BAZ', line=4, col=19)
    Token(type=RIGHT_PAREN, content=')', line=4, col=22)
    Token(type=RIGHT_PAREN, content=')', line=4, col=23)
    Token(type=NEWLINE, content='\n', line=4, col=24)
    Token(type=WHITESPACE, content='  ', line=5, col=0)
    Token(type=WORD, content='add_library', line=5, col=2)
    Token(type=LEFT_PAREN, content='(', line=5, col=13)
    Token(type=WORD, content='hello', line=5, col=14)
    Token(type=WHITESPACE, content=' ', line=5, col=19)
    Token(type=UNQUOTED_LITERAL, content='hello.cc', line=5, col=20)
    Token(type=RIGHT_PAREN, content=')', line=5, col=28)
    Token(type=NEWLINE, content='\n', line=5, col=29)
    Token(type=WORD, content='endif', line=6, col=0)
    Token(type=LEFT_PAREN, content='(', line=6, col=5)
    Token(type=RIGHT_PAREN, content=')', line=6, col=6)
    Token(type=NEWLINE, content='\n', line=6, col=7)

.. dynamic: dump-example-lex-end

-------------------
Parser: Syntax Tree
-------------------

``cmake-format`` parses the token stream in a single pass.
The state machine of the parser is maintained by the program stack
(i.e. the parse functions are called recursively) and each node type in the
tree has it's own parse function.

There are fourteen types of nodes in the parse tree. They are described below
along with the list of possible child node types.


Node Types
==========

+--------------+---------------------------------------------+----------------+
| Node Type    | Description                                 | Allowed        |
|              |                                             | Children       |
+--------------+---------------------------------------------+----------------+
| BODY         | A generic section of a cmake document. This | COMMENT        |
|              | node type is found at the root of the parse | STATEMENT      |
|              | tree and within conditional/flow control    | WHITESPACE     |
|              | statements                                  |                |
|              |                                             |                |
+--------------+---------------------------------------------+----------------+
| WHITESPACE   | A consecutive sequence of whitespace tokens | (none)         |
|              | between any two other types of nodes.       |                |
+--------------+---------------------------------------------+----------------+
| COMMENT      | A sequence of one or more comment lines.    | (token)        |
|              | The node consistes of all consecutive       |                |
|              | comment lines unbroken by additional        |                |
|              | newlines or a single BRACKET_COMMENT token. |                |
+--------------+---------------------------------------------+----------------+
| STATEMENT    | A cmake statement (i.e. function call)      | ARGGROUP       |
|              |                                             | COMMENT        |
|              |                                             | FUNNAME        |
+--------------+---------------------------------------------+----------------+
| FLOW_CONTROL | Two or more cmake statements and their      | STATEMENT      |
|              | nested bodies representing a flow control   | BODY           |
|              | construct (i.e. ``if`` or ``foreach``).     |                |
+--------------+---------------------------------------------+----------------+
| ARGGROUP     | A top-level collection of one or more       | PARGGROUP      |
|              | positional, kwarg, or flag groups           | KWARGGROUP     |
|              |                                             | PARENGROUP     |
|              |                                             | FLAGGROUP      |
|              |                                             | COMMENT        |
+--------------+---------------------------------------------+----------------+
| PARGGROUP    | A grouping of one or more positional        | ARGUMENT       |
|              | arguments.                                  | COMMENT        |
+--------------+---------------------------------------------+----------------+
| FLAGGROUP    | A grouping of one or more positional        | FLAG           |
|              | arguments, each of which is a flag          | COMMENT        |
+--------------+---------------------------------------------+----------------+
| KWARGGROUP   | A KEYWORD group, starting with the keyword  | KEYWORD        |
|              | and ending with the last argument associated| ARGGROUP       |
|              | with that keyword                           |                |
+--------------+---------------------------------------------+----------------+
| PARENGROUP   | A parenthetical group, starting with a left | ARGGROUP       |
|              | parenthesis and ending with the matching    |                |
|              | right parenthesis                           |                |
+--------------+---------------------------------------------+----------------+
| FUNNAME      | Consists of a single token containing the   | (token)        |
|              | name of the function/command in a statement |                |
|              | with that keyword                           |                |
+--------------+---------------------------------------------+----------------+
| ARGUMENT     | Consists of a single token, containing the  | (token)        |
|              | literal argument of a statement, and        | COMMENT        |
|              | optionally a comment associated with it     |                |
+--------------+---------------------------------------------+----------------+
| KEYWORD      | Consists of a single token, containing the  | (token)        |
|              | literal keyword of a keyword group, and     | COMMENT        |
|              | optionally a comment associated with it     |                |
+--------------+---------------------------------------------+----------------+
| FLAG         | Consists of a single token, containing the  | (token)        |
|              | literal keyword of a statment flag, and     | COMMENT        |
|              | optionally a comment associated with it     |                |
+--------------+---------------------------------------------+----------------+
| ONOFFSWITCH  | Consists of a single token, containing the  | (token)        |
|              | sentinal comment line ``# cmake-format: on``|                |
|              | or ``# cmake-format: off``.                 |                |
+--------------+---------------------------------------------+----------------+

You can inspect the parse tree of a listfile by ``cmake-format`` with
``--dump parse``. For example:

.. dynamic: dump-example-parse-begin

.. code:: text

    └─ BODY: 1:0
        ├─ WHITESPACE: 1:0
        │   └─ Token(type=NEWLINE, content='\n', line=1, col=0)
        ├─ STATEMENT: 2:0
        │   ├─ FUNNAME: 2:0
        │   │   └─ Token(type=WORD, content='cmake_minimum_required', line=2, col=0)
        │   ├─ LPAREN: 2:22
        │   │   └─ Token(type=LEFT_PAREN, content='(', line=2, col=22)
        │   ├─ ARGGROUP: 2:23
        │   │   └─ KWARGGROUP: 2:23
        │   │       ├─ KEYWORD: 2:23
        │   │       │   └─ Token(type=WORD, content='VERSION', line=2, col=23)
        │   │       ├─ Token(type=WHITESPACE, content=' ', line=2, col=30)
        │   │       └─ ARGGROUP: 2:31
        │   │           └─ PARGGROUP: 2:31
        │   │               └─ ARGUMENT: 2:31
        │   │                   └─ Token(type=UNQUOTED_LITERAL, content='3.5', line=2, col=31)
        │   └─ RPAREN: 2:34
        │       └─ Token(type=RIGHT_PAREN, content=')', line=2, col=34)
        ├─ WHITESPACE: 2:35
        │   └─ Token(type=NEWLINE, content='\n', line=2, col=35)
        ├─ STATEMENT: 3:0
        │   ├─ FUNNAME: 3:0
        │   │   └─ Token(type=WORD, content='project', line=3, col=0)
        │   ├─ LPAREN: 3:7
        │   │   └─ Token(type=LEFT_PAREN, content='(', line=3, col=7)
        │   ├─ ARGGROUP: 3:8
        │   │   └─ PARGGROUP: 3:8
        │   │       └─ ARGUMENT: 3:8
        │   │           └─ Token(type=WORD, content='demo', line=3, col=8)
        │   └─ RPAREN: 3:12
        │       └─ Token(type=RIGHT_PAREN, content=')', line=3, col=12)
        ├─ WHITESPACE: 3:13
        │   └─ Token(type=NEWLINE, content='\n', line=3, col=13)
        ├─ FLOW_CONTROL: 4:0
        │   ├─ STATEMENT: 4:0
        │   │   ├─ FUNNAME: 4:0
        │   │   │   └─ Token(type=WORD, content='if', line=4, col=0)
        │   │   ├─ LPAREN: 4:2
        │   │   │   └─ Token(type=LEFT_PAREN, content='(', line=4, col=2)
        │   │   ├─ ARGGROUP: 4:3
        │   │   │   ├─ PARGGROUP: 4:3
        │   │   │   │   ├─ ARGUMENT: 4:3
        │   │   │   │   │   └─ Token(type=WORD, content='FOO', line=4, col=3)
        │   │   │   │   └─ Token(type=WHITESPACE, content=' ', line=4, col=6)
        │   │   │   └─ KWARGGROUP: 4:7
        │   │   │       ├─ KEYWORD: 4:7
        │   │   │       │   └─ Token(type=WORD, content='AND', line=4, col=7)
        │   │   │       ├─ Token(type=WHITESPACE, content=' ', line=4, col=10)
        │   │   │       └─ ARGGROUP: 4:11
        │   │   │           └─ PARENGROUP: 4:11
        │   │   │               ├─ LPAREN: 4:11
        │   │   │               │   └─ Token(type=LEFT_PAREN, content='(', line=4, col=11)
        │   │   │               ├─ ARGGROUP: 4:12
        │   │   │               │   ├─ PARGGROUP: 4:12
        │   │   │               │   │   ├─ ARGUMENT: 4:12
        │   │   │               │   │   │   └─ Token(type=WORD, content='BAR', line=4, col=12)
        │   │   │               │   │   └─ Token(type=WHITESPACE, content=' ', line=4, col=15)
        │   │   │               │   └─ KWARGGROUP: 4:16
        │   │   │               │       ├─ KEYWORD: 4:16
        │   │   │               │       │   └─ Token(type=WORD, content='OR', line=4, col=16)
        │   │   │               │       ├─ Token(type=WHITESPACE, content=' ', line=4, col=18)
        │   │   │               │       └─ ARGGROUP: 4:19
        │   │   │               │           └─ PARGGROUP: 4:19
        │   │   │               │               └─ ARGUMENT: 4:19
        │   │   │               │                   └─ Token(type=WORD, content='BAZ', line=4, col=19)
        │   │   │               └─ RPAREN: 4:22
        │   │   │                   └─ Token(type=RIGHT_PAREN, content=')', line=4, col=22)
        │   │   └─ RPAREN: 4:23
        │   │       └─ Token(type=RIGHT_PAREN, content=')', line=4, col=23)
        │   ├─ BODY: 4:24
        │   │   ├─ WHITESPACE: 4:24
        │   │   │   ├─ Token(type=NEWLINE, content='\n', line=4, col=24)
        │   │   │   └─ Token(type=WHITESPACE, content='  ', line=5, col=0)
        │   │   ├─ STATEMENT: 5:2
        │   │   │   ├─ FUNNAME: 5:2
        │   │   │   │   └─ Token(type=WORD, content='add_library', line=5, col=2)
        │   │   │   ├─ LPAREN: 5:13
        │   │   │   │   └─ Token(type=LEFT_PAREN, content='(', line=5, col=13)
        │   │   │   ├─ ARGGROUP: 5:14
        │   │   │   │   ├─ PARGGROUP: 5:14
        │   │   │   │   │   ├─ ARGUMENT: 5:14
        │   │   │   │   │   │   └─ Token(type=WORD, content='hello', line=5, col=14)
        │   │   │   │   │   └─ Token(type=WHITESPACE, content=' ', line=5, col=19)
        │   │   │   │   └─ PARGGROUP: 5:20
        │   │   │   │       └─ ARGUMENT: 5:20
        │   │   │   │           └─ Token(type=UNQUOTED_LITERAL, content='hello.cc', line=5, col=20)
        │   │   │   └─ RPAREN: 5:28
        │   │   │       └─ Token(type=RIGHT_PAREN, content=')', line=5, col=28)
        │   │   └─ WHITESPACE: 5:29
        │   │       └─ Token(type=NEWLINE, content='\n', line=5, col=29)
        │   └─ STATEMENT: 6:0
        │       ├─ FUNNAME: 6:0
        │       │   └─ Token(type=WORD, content='endif', line=6, col=0)
        │       ├─ LPAREN: 6:5
        │       │   └─ Token(type=LEFT_PAREN, content='(', line=6, col=5)
        │       ├─ ARGGROUP: 0:0
        │       └─ RPAREN: 6:6
        │           └─ Token(type=RIGHT_PAREN, content=')', line=6, col=6)
        └─ WHITESPACE: 6:7
            └─ Token(type=NEWLINE, content='\n', line=6, col=7)

.. dynamic: dump-example-parse-end

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
``--dump layout``. For example:

.. dynamic: dump-example-layout-begin

.. code:: text

    └─ BODY,(passno=0,wrap=F,ok=T) pos:(0,0) colextent:35
        ├─ STATEMENT,(passno=0,wrap=F,ok=T) pos:(0,0) colextent:35
        │   ├─ FUNNAME,(passno=0,wrap=F,ok=T) pos:(0,0) colextent:22
        │   ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(0,22) colextent:23
        │   ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(0,23) colextent:34
        │   │   └─ KWARGGROUP,(passno=0,wrap=F,ok=T) pos:(0,23) colextent:34
        │   │       ├─ KEYWORD,(passno=0,wrap=F,ok=T) pos:(0,23) colextent:30
        │   │       └─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(0,31) colextent:34
        │   │           └─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(0,31) colextent:34
        │   │               └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(0,31) colextent:34
        │   └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(0,34) colextent:35
        ├─ STATEMENT,(passno=0,wrap=F,ok=T) pos:(1,0) colextent:13
        │   ├─ FUNNAME,(passno=0,wrap=F,ok=T) pos:(1,0) colextent:7
        │   ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(1,7) colextent:8
        │   ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(1,8) colextent:12
        │   │   └─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(1,8) colextent:12
        │   │       └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(1,8) colextent:12
        │   └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(1,12) colextent:13
        └─ FLOW_CONTROL,(passno=0,wrap=F,ok=T) pos:(2,0) colextent:29
            ├─ STATEMENT,(passno=0,wrap=F,ok=T) pos:(2,0) colextent:24
            │   ├─ FUNNAME,(passno=0,wrap=F,ok=T) pos:(2,0) colextent:2
            │   ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(2,2) colextent:3
            │   ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,3) colextent:23
            │   │   ├─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,3) colextent:6
            │   │   │   └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(2,3) colextent:6
            │   │   └─ KWARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,7) colextent:23
            │   │       ├─ KEYWORD,(passno=0,wrap=F,ok=T) pos:(2,7) colextent:10
            │   │       └─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,11) colextent:23
            │   │           └─ PARENGROUP,(passno=0,wrap=F,ok=T) pos:(2,11) colextent:23
            │   │               ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(2,11) colextent:12
            │   │               ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,12) colextent:22
            │   │               │   ├─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,12) colextent:15
            │   │               │   │   └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(2,12) colextent:15
            │   │               │   └─ KWARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,16) colextent:22
            │   │               │       ├─ KEYWORD,(passno=0,wrap=F,ok=T) pos:(2,16) colextent:18
            │   │               │       └─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,19) colextent:22
            │   │               │           └─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(2,19) colextent:22
            │   │               │               └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(2,19) colextent:22
            │   │               └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(2,22) colextent:23
            │   └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(2,23) colextent:24
            ├─ BODY,(passno=0,wrap=F,ok=T) pos:(3,2) colextent:29
            │   └─ STATEMENT,(passno=0,wrap=F,ok=T) pos:(3,2) colextent:29
            │       ├─ FUNNAME,(passno=0,wrap=F,ok=T) pos:(3,2) colextent:13
            │       ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(3,13) colextent:14
            │       ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(3,14) colextent:28
            │       │   ├─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(3,14) colextent:19
            │       │   │   └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(3,14) colextent:19
            │       │   └─ PARGGROUP,(passno=0,wrap=F,ok=T) pos:(3,20) colextent:28
            │       │       └─ ARGUMENT,(passno=0,wrap=F,ok=T) pos:(3,20) colextent:28
            │       └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(3,28) colextent:29
            └─ STATEMENT,(passno=0,wrap=F,ok=T) pos:(4,0) colextent:7
                ├─ FUNNAME,(passno=0,wrap=F,ok=T) pos:(4,0) colextent:5
                ├─ LPAREN,(passno=0,wrap=F,ok=T) pos:(4,5) colextent:6
                ├─ ARGGROUP,(passno=0,wrap=F,ok=T) pos:(4,6) colextent:6
                └─ RPAREN,(passno=0,wrap=F,ok=T) pos:(4,6) colextent:7

.. dynamic: dump-example-layout-end

------------
Example file
------------

The example file used to create the tree dumps above is:::

    cmake_minimum_required(VERSION 3.5)
    project(demo)
    if(FOO AND (BAR OR BAZ))
      add_library(hello hello.cc)
    endif()
