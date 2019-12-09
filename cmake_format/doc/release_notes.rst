=============
Release Notes
=============

Details of changes can be found in the changelog, but this file will contain
some high level notes and highlights from each release.

v0.6 series
===========

------
v0.6.3
------

This release finally includes some progress on a long-standing goal: a
`cmake-linter`__ built on the same foundation as the formatter. As of this
release The ``cmake-format`` python package now comes with both the
``cmake-format`` and ``cmake-lint`` programs. The linter is still in a
relatively early state and lacks many features, but should continue to grow
with the formatter in future releases.

Along with the new linter, this release also includes some reorganization
of the documentation in order to more clearly separate information about
the different programs that are distributed from this repository.

.. __: https://cmake-format.readthedocs.io/en/latest/cmake-lint.html

------
v0.6.2
------

This is a maintenance release. Some additional command parsers have
moved out of the standard parse model improving the parse of these
commands. This release also includes some groundwork scripts to parse
the usage strings in the cmake help text. Additionally:

* ``--in-place`` will preserve file mode
* The new ``--check`` command line option will not format the file, but
  exit with non-zero status if any changes would be made
* The new ``--require-valid-layout`` option will exit with non-zero status
  if an admissible layout is not found.

------
v0.6.1
------

This is primarily a documentation update. Some of the testing infrastructure
has changed but no user-facing code has been modified.

------
v0.6.0
------

This release includes a significant refactor of the formatting logic. Details
of the new algorithm are described in the documentation__. As a result of the
algorithm changes, some config options have changed too. The following
config options are removed:

* ``max_subargs_per_line`` (see ``max_pargs_hwrap``)
* ``nest_threshold`` (see ``min_prefix_chars``)
* ``algorithm_order`` (see ``layout_passes``)

.. __: https://cmake-format.readthedocs.io/en/latest/format_algorithm.html

And the following config options have been added:

* ``max_subgroups_hwrap``
* ``max_pargs_hwrap``
* ``dangle_align``
* ``min_prefix_chars``
* ``max_prefix_chars``
* ``max_lines_hwrap``
* ``layout_passes``
* ``enable_sort``

Also as a result of the algorithm changes, the default layout has changed. By
default, ``cmake-format`` will now prefer to nest long lists rather than
aligning them to the opening parenthesis of a statement. Also, due to the new
configuration options, the output of ``cmake-format`` is likely to be different
with your current configs.

Additionally, ``cmake-format`` will now tend to prefer a normal "horizontal"
wrap for relatively long lists of positional arguments (e.g. source files in
``add_library``) whereas it would previously prefer a vertical layout (one-entry
per line). This is a consequence of an ambiguity between which positional
arguments should be vertical versus which should be wrapped. Two planned
features (layout tags and positional semantics) should help to provide enough
control to get the layout you want in these lists.

I acknowledge that it is not ideal for formatting to change between releases
but this is an unfortunate inevitability at this stage of development. The
changes in this release elminate a number of inconsistencies and also adds the
groundwork for future planned features and options. Hopefully we are getting
close to a stable state and a 1.0 release.

v0.5 series
===========

------
v0.5.5
------

This is a maintenance release fixing a few minor bugs and enhancements. One
new feature is that the ``--config`` command line option now accepts a list of
config files, which should allow for including multiple databases of command
specifications
------
v0.5.4
------

This is a maintenance release fixing a couple of bugs and adding some missing
documentation. One notable feature added is that, during in-place formatting,
if the file content is unchanged ``cmake-format`` will no-longer write the
file.

------
v0.5.3
------

This hotfix release fixes a bug that would crash cmake-format if no
configuration file was present. It also includes some small under-the-hood
changes in preparation for an overhaul of the formatting logic.


------
v0.5.2
------

This release fixes a few bugs and does some internal prep work for upcoming
format algorithm changes. The documentation on the format algorithm is a little
ahead of the code state in this release. Also, the documentation theme has
changed to something based on read-the-docs (I hope you like it).

* Add missing forms of ``add_library()`` and ``add_executable()``
* ``--autosort`` now defaults to ``False`` (it can be somewhat suprising) and
  it doesn't always get it right.
* Configuration options in ``--help`` and in the example configurations from
  ``--dump-config`` are now split into hopefully meaningful sections.
* ``cmake-format`` no longer tries to infer "keywords" or "flags" from
  ``COMMAND`` strings. This matching wasn't good enough as there is way too
  much variance in how programs design their command line options.

------
v0.5.1
------

The 0.5.0 release involved some pretty big changes to the parsing engine and
introduced a new format algorithm. These two things combined unfortunately
lead to a lot of new bugs. The full battery of pre-release tests wasn't run
and so a lot of those issues popped up after release. Hopefully most of those
are squashed in this release.

* Fixed lots of bugs introduced in 0.5.0
* ``cmake-format`` has a channel on discord now. Come chat about it at
  https://discord.gg/NgjwyPy

------
v0.5.0
------

* Overhauled the parser logic enabling arbitrary implementations of statement
  parsers. The generic statement parser is now implemented by the
  ``standard_parse`` function (or the ``StandardParser`` functor, which is used
  to load legacy ``additional_commands``).
* New custom parser logic for deep cmake statements such as:

  * ``install``
  * ``file``
  * ``ExternalProject_XXX``
  * ``FetchContent_XXX``

* ``cmake-format`` can now sort your argument lists for you (such as lists
  of files). This enabled with the ``autosort`` config option. Some argument
  lists are inherently sortable (e.g. the list of sources supplied to
  ``add_library`` or ``add_executable``). Other commands (e.g. ``set()`` which
  cannot be inferred sortable can be explicitly tagged using a comment at the
  beginning of the list. See the README for more information.
* A consequence of the above is that the parse tree for ``set()`` has changed,
  and so it's default formatting in many cases has also changed. You can
  restore the old behavior by adding the following to your config::

      additional_commands = {
        "set": {
          "flags": ["FORCE", "PARENT_SCOPE"],
          "kwargs": {
            "CACHE": "*"
          }
        }
      }

* The default command case has changed from ``lower`` to ``canonical``
  (which is a new option). In most cases this is the same as ``lower`` but for
  some standard, non-builtin commands the canonical spelling is
  CamelCase (i.e. ``ExternalProject_Add``).
* There is a new ``cmake-annotate`` program distributed with the package. It
  can generate semantic HTML renderings of your listfiles (see the
  documentation for details).

v0.4 series
===========

------
v0.4.5
------

* Add travis CI configuration for public github repo

------
v0.4.4
------

* Add the ability to dump out markup parse lists for debugging.
* Add the ability to dump out a semantic HTML markup of a listfile, allowing
  for easy server-side semantic highlighting of documentation pages.
  See :ref:`render_html`.

------
v0.4.2
------

* Added the brand new ``Visual Studio Code`` extension, which can be found in
  the ``vscode`` marketplace! You can now use ``cmake-format`` to
  "Format Document" in `vscode`.
* Some new configuration options to allow user-specified literal fences and
  rulers in comment markup.
* New configuration options to preserve literal comment blocks at the start of
  your listfiles (intended for copyright statements), as well as to disable
  comment reflow alltogether.
* Fixed some bugs and improved some error messages

Enjoy!
