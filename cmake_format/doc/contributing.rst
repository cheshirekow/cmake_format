============================
Contributing to cmake-format
============================

-------------
General Rules
-------------

1. Please use ``pylint`` and ``flake8`` to check your code for lint. There are
   config files in the repo.
2. There is a python ``unittest`` suite in ``cmake_formattests.py``. Run with
   ``python -Bm cmake_format.tests`` (ensure modified code is on the python
   path). Alternatively you can use ``cmake`` (``make test``, ``ninja test``,
   etc) or bazel (``bazel test ...``).
3. There's an ``autopep8`` config file in the repo as well. Feel free to use
   that to format the code. Note that ``autopep8`` and ``pylint`` disagree
   in a few places so using ``autopep8`` may require some manual edits
   afterward.

-------------
Build Systems
-------------

You don't need to "build" ``cmake-format``, but there are ``cmake`` and
``bazel`` build rules that you can use if you find it convenient. For the
most part your contribution is in good shape if the ``test`` and ``lint``
(cmake) build targets pass or, equivalently, if ``bazel test ...`` passes.
If you add new files to the repository, please update the corresponding
``CMakeLists.txt`` and ``BUILD`` files to keep the lint and test configurations
up to date.

-------------
Sidecar Tests
-------------

Whether or not to write your tests in cmake or in python will depend largely on
the test. If you simply want to assert that a particular snippet of code is
formatted in a specific way, writing the test in cmake is most natural. If any
logic is needed, then writing in the body of a python function makes the most
sense.

Test written in cmake are stored in ``.cmake`` sidecar files associated with
python ``unittest`` cases (see ``command_tests/*``).


The format of these tests are very simple. The test begins with a line comment
in the form of::

   # test: <test-name>

And ends with the start of the next test, the end of the file, or a line
comment in the form of::

   # end-test

If non-default configuration options are required, or if you would like to
assert a lex, parse, or layout result, then you can specify that in an optional
bracket comment immediately following the ``# test: `` sentinel. The bracket
comment must begin and end on it's own line, such as::

   #[=[
      line_width = 10
   ]=]

The content of the comment is parsed as python and variables are interpreted as
configuration variables, except for the following:

* expect_lex - a list of lexer tokens indicated the expected lex result
* expect_parse - a tree of parse node names indicated the expected parse tree
  structure
* expect_layout - a tree of layout node names and geometries indicated the
  expected layout result.

A test called ``test_<test-name>`` will be generated at runtime. The test will
involve ``cmake-format`` formatting the code snippet using the default
configuration, and asserting that the output matches the input.

---------
Debugging
---------

Formatting
==========

For the most part, cmake-format ignores white-space when it parses the list
file into the parse tree so most of the formatting tests can
be restricted to "idempotency" tests. In other words, you write down the
listfile code in the format you expect and if ``cmake-format`` doesn't change
it, the test passes.

Lexing, Parsing, Layout
=======================

If you suspect a problem with the lexing, parsing, or layout algorithms,
try to create a minimial working example of the problem, and use the
``--dump [lex|parse|layout]`` command line option to inspect the output of the
different phases.

Once you've identified the problem, the best thing to do is create a test
asserting an expected output at the problematic phase. You can start by
asserting an empty output. For example, something like:

.. code:: cmake

   # test: debug_my_case
   #[=[
     expect_lex = []
   ]=]
   if(something)
     your_cmake_code_here(foo bar baz)
   else()

The test will fail, but the error message will print out the actual result.
In the example above::

   Second list contains 19 additional elements.
   First extra element 0:
   TokenType.WORD

   - []
   + [TokenType.WORD,
   +  TokenType.LEFT_PAREN,
   +  TokenType.WORD,
   +  TokenType.RIGHT_PAREN,
   +  TokenType.NEWLINE,
   +  TokenType.WHITESPACE,
   +  TokenType.WORD,
   +  TokenType.LEFT_PAREN,
   +  TokenType.WORD,
   +  TokenType.WHITESPACE,
   +  TokenType.WORD,
   +  TokenType.WHITESPACE,
   +  TokenType.WORD,
   +  TokenType.RIGHT_PAREN,
   +  TokenType.NEWLINE,
   +  TokenType.WORD,
   +  TokenType.LEFT_PAREN,
   +  TokenType.RIGHT_PAREN,
   +  TokenType.NEWLINE]

You can copy-paste the actual output as the expected output as a starting
point for your test. You can modify the "expected" specification to match what
the output *should* be. Then, as you iterate, you can use the test to know when
you've fixed the problem.

-------------
Pull Requests
-------------

Feel free to make a pull request on github, though please take note of the
following rules and guidelines. These rules are enforced through the travis
CI builds so if travis passes your submission is probably in good shape.

Squash your feature
===================

Please squash your changes when issuing a pull request so that the request is
for a single commit. This helps us move the patch from the public github mirror
into the upstream respository. When updating your request, please squash
additional commits (you will likely need to force-push to your feature branch).

Rebase before submit
====================

Please rebase your patch on the current HEAD before submitting the pull request.
This helps us to keep a tidy history. When we merge your commit we don't want
to create graph connections across long regions of the git history. Travis will
fail any pull request which is more than 10 commits behind the HEAD.

Sign your commit
================

When making a pull request, please sign the commit  (use ``git commit -S``).

Sign the copyright assignment
=============================

Please sign the copyright assignment agreement (details below) using the same
PGP key you use to sign the commit, and please ensure that the key is available
on the popular keyservers. Travis will fetch it from
https://keyserver.ubuntu.com

.. _copyright:
--------------------
Copyright Assignment
--------------------

To sign the copyright assignment agreement the quick way, run::

   python -Bm cmake_format.contrib.sign_ca

from the root of the repository.

For the long way, please follow this process:

1. Copy the file ``cmake_format/contrib/individual_ca.txt`` to some working
   directory as, e.g., ``cmake-format-ca.txt.in``.

2. Replace the template strings at the bottom with your actual name and
   email address.

3. Sign the document with e.g.::

   gpg --output cmake-format-ca.txt --clearsign cmake-format-ca.txt.in``

   Please be sure to use the same pgp key that you'll be using to sign your
   commits.

4. Copy the asci-armored signature packet at the bottom of the signed document
   and paste it into ``cmake_format/contrib/signature_db.json``. Include this
   change in your first pull request.

-------------------------
Un-Assigned contributions
-------------------------

In general, copyright for contributions should be assigned to the project.
This should keep everything on the level should we find the need to offer
``cmake-format`` though additional licenses in the future.

If you'd like to make a significant contribution to ``cmake-format`` but don't
agree to the terms of the copyright assignment please contact us to set up an
alternate agreement. Otherwise, please consider filing a feature-request for
changes you would like to see implemented.
