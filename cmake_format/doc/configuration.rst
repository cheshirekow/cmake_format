.. _configuration:

=============
Configuration
=============

The different tools utilize a common parsing core and so share a
common configuration system and in fact can share the same configuration
file(s).

The tools accept configuration files in yaml, json, or python format.

.. note::

  In order to read your configuration files in YAML format, the
  tools require the ``pyyaml`` python package to be installed. This
  dependency is not enforced by default during installation since this
  is an optional feature. It can be enabled by installing with a
  command like ``pip install cmake_format[YAML]``. Or you can install
  ``pyyaml`` manually.


You may specify a path to one or more configuration files with the
``--config-file`` (``--config-files``) command line option. Otherwise, the
tools will search the ancestry of each source file looking for a configuration
file to use. If no configuration file is found it will use sensible defaults.

Automatically detected configuration files may have any name that matches
``\.?cmake-format(.yaml|.json|.py)``.

If you'd like to create a new configuration file, ``cmake-format`` can help
by dumping out the default configuration in your preferred format. You can run
``cmake-format --dump-config [python|json|yaml]`` to print the default
configuration to ``stdout`` and use that as a starting point.

.. warning::

  ``cmake-format`` will detect and load an automatic configuration file, even
  when executing ``--dump-config``. This is so that you can debug the *active*
  configuration from a certain location in your tree. If you have a corrupt /
  un-parsable configuration file in an automatic location ``--dump-config`` may
  fail. You can always ``cd`` to a clean location (``/`` or ``/tmp``) and
  execute ``--dump-config`` to get a default configuration.

Here is an example python-style configuration file with the default options and
help-text. Some detailed explanation and examples can be found at
:ref:`configopts`.

.. literalinclude:: bits/configbits.py
