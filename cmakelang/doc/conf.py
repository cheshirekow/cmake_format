import importlib
import os

# Source the common stuff
with open(os.path.join("./conf_common.py")) as infile:
  exec(infile.read())  # pylint: disable=W0122

_module = importlib.import_module("cmakelang")

# Override the project-specific stuff
project = "cmakelang"
docname = project + u'doc'
title = project + ' Documentation'
version = _module.__version__
release = _module.__version__
