import importlib
import os

this_file = os.path.realpath(__file__)
this_dir = os.path.dirname(this_file)
_ = os.path.dirname(this_dir)
root_dir = os.path.dirname(_)

with open(os.path.join(root_dir, "doc/conf.py")) as infile:
  exec(infile.read())  # pylint: disable=W0122

project = "cmake_format"
module = importlib.import_module(project)

docname = project + u'doc'
title = project + ' Documentation'
version = module.VERSION
release = module.VERSION

html_static_path = [os.path.join(root_dir, "doc/sphinx-static")]
