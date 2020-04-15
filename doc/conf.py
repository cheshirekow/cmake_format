# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sphinx_rtd_theme

project = 'tangentsky'
thisfile = os.path.realpath(__file__)
rootdir = globals().get(
    "rootdir", os.sep.join(thisfile.split(os.sep)[:-3]))

if os.environ.get("READTHEDOCS") == "True":
  # Do any RTD-specific setup here
  pass

# General information about the project.
docname = project + u'doc'
title = project + ' Documentation'
copyright = u'2018-2019, Josh Bialkowski'  # pylint: disable=W0622
author = u'Josh Bialkowski'

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    # autosectionlabel is pretty broken
    # 'sphinx.ext.autosectionlabel',
    # "readthedocs_ext.readthedocs",
]

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

mathjax_path = (
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/"
    "2.7.5/MathJax.js?config=TeX-MML-AM_CHTML")

# Add any paths that contain templates here, relative to this directory.
templates_path = []

source_suffix = ['.rst']
master_doc = 'index'

version = u'0.1.0'
release = u'0.1.0'
language = None
exclude_patterns = [
    '.sphinx_build',
    'Thumbs.db',
    '.DS_Store'
]

pygments_style = 'sphinx'
todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
# html_theme = "alabaster"
numfig = True
math_numfig = True
math_number_all = True
math_eqref_format = "Eq. {number}"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "collapse_navigation": True,
    "display_version": True,
    "sticky_navigation": True,
}

html_static_path = ["sphinx-static"]
html_style = "css/cheshire_theme.css"

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'globaltoc.html',  # NOTE(josh): added
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

htmlhelp_basename = project + 'doc'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, project + '.tex', title, author, 'manual'),
]

man_pages = [
    (master_doc, project, title,
     [author], 1)
]

texinfo_documents = [
    (master_doc, project, title,
     author, project, 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/': None}
