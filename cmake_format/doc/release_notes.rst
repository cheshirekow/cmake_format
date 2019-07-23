=============
Release Notes
=============

Details of changes can be found in the changelog, but this file will contain
some high level notes and highlights from each release.

v0.5 series
===========

------
v0.5.3
------

This is a maintanance release fixing a couple of bugs and adding some missing
documentation. One notable feature added is that, during in-place formatting,
if the file content is unchanged ``cmake-format`` will no-longer write the
file.

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
