=========
Changelog
=========

-------
v0.2.0
-------

* add unit tests using python unit test framework
* accept configuration as yaml or json
* Implemented custom cmake AST parser, getting rid of dependency on cmlp
* Removed static global command configuration
* If no configuration file specified, search for a file based on the input
  file path.
* Moved code out of ``__main__.py`` and into modules
* More documentation and general cleanup
* Add ``setup.py``
* Tested on a production codebase with 350+ listfiles and a manual scan of
  changes looked good, and the build seems to be healthy.
