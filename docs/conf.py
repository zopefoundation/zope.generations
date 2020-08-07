# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sys
import os
import pkg_resources
sys.path.append(os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('.'))
rqmt = pkg_resources.require('zope.generations')[0]


# -- Project information -----------------------------------------------------

project = 'zope.generations'
copyright = '2020, Zope Community'
author = 'Zope Community'


# -- General configuration ---------------------------------------------------
# If your documentation needs a minimal Sphinx version, state it here.
#

# 1.8 was the last version that runs on Python 2; 2.0+ requires Python 3.
# `autodoc_default_options` was new in 1.8
needs_sphinx = "1.8"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'repoze.sphinx.autointerface',

]
master_doc = 'index'
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '%s.%s.%s' % tuple(map(int, rqmt.version.split('.')[:3]))
# The full version, including alpha/beta/rc tags.
release = rqmt.version

# The reST default role (used for this markup: `text`) to use for all
# documents.
#
default_role = 'obj'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

intersphinx_mapping = {
    'https://docs.python.org/': None,
    'https://zodb-docs.readthedocs.io/en/latest/': None,
    'https://persistent.readthedocs.io/en/latest/': None,

    'https://zopecomponent.readthedocs.io/en/latest/': None,
    'https://zopeconfiguration.readthedocs.io/en/latest/': None,
    'https://zopeevent.readthedocs.io/en/latest/': None,
    'https://zopeinterface.readthedocs.io/en/latest/': None,
    'https://zopeprocesslifetime.readthedocs.io/en/latest/': None,
}


# Sphinx 1.8+ prefers this to `autodoc_default_flags`. It's documented that
# either True or None mean the same thing as just setting the flag, but
# only None works in 1.8 (True works in 2.0)
autodoc_default_options = {
    'members': None,
    'show-inheritance': None,
}
autodoc_member_order = 'bysource'
autoclass_content = 'both'
