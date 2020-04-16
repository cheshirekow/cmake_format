============
Installation
============

All of the tools are included as part of the ``cmake-format`` python
distribution package.

Install with pip
================

The easiest way to install ``cmake-format`` is from `pypi.org`_
using `pip`_. For example::

    pip install cmake_format

If you're on a linux-type system (such as ubuntu) the above command might not
work if it would install into a system-wide location. If that's what you
really want you might need to use :code:`sudo`, e.g.::

    sudo pip install cmake_format

In general though I wouldn't really recommend doing that though since things
can get pretty messy between your system python distributions and your
:code:`pip` managed directories. Alternatively you can install it for your user
with::

    pip install --user cmake_format

which I would probably recommend for most users.

.. note::

   If you wish to use a configuration file in YAML format you'll want to
   install with the optional ``YAML`` feature, e.g.::

       pip install cmake_format[YAML]

.. _`pypi.org`: https://pypi.org/project/cmake-format/
.. _pip: https://pip.pypa.io/en/stable/

Install from source
===================

You can also install from source with pip. You can download a release package
from github__ or pypi__ and then install it directly with pip. For example::

  pip install v0.6.10.tar.gz

.. __: https://github.com/cheshirekow/cmake_format/releases
.. __: https://pypi.org/project/cmake-format/#files

Note that the release packages on github are automatically generated from git
tags which are the same commit used to generate the corresponding version
package on ``pypi.org``. So whether you install a particular version from
github or pypi shouldn't matter.

Pip can also install directly from github. For example::

    pip install git+https://github.com/cheshirekow/cmake_format.git

If you wish to test a pre-release or dev package from a branch called
``foobar`` you can install it with::

    pip install "git+https://github.com/cheshirekow/cmake_format.git@foobar"

IDE Integrations
================

For the formatter specifically:

* There is an official `vscode extension`__
* Someone also created a `sublime plugin`__

.. __: https://marketplace.visualstudio.com/items?itemName=cheshirekow.cmake-format
.. __: https://packagecontrol.io/packages/CMakeFormat

Note that for both plugins ``cmake-format`` itself must be installed
separately.

Pre-commit
==========

If you are a user of the `pre-commit`__ project you can easily add the
formatter, ``cmake-format``, to your hooks with the following addition to your
``.pre-commit-hooks.yaml`` file.

.. __: https://pre-commit.com/

.. code:: yaml

   repos:
     - repo: https://github.com/cheshirekow/cmake-format-precommit
       rev: v0.6.10
       hooks:
       - id: cmake-format
