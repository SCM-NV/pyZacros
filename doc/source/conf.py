# -*- coding: utf-8 -*-
#
# pyZacros documentation build configuration file
# This conf.py file is meant to be used within SCM's userdoc setups.

from pathlib import Path
import sys

def setup(app):
    # For sphinx autodoc, we need the pyzacros module in the path.
    # So, here we add it to the path (in a quite hackish way...)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

if not tags.has('scm_theme'):
    sys.exit("This conf.py file is for building the documentation within SCM's setups. You need the scm_theme and the SCM global_conf." )

from global_conf import *

project, htmlhelp_basename, latex_documents = set_project_specific_var ('pyZacros')

# html_logo = '_static/pyZacros_logo_compact.svg'

extensions += [
    'sphinx.ext.autodoc',
]

# Avoid duplicate names by prefixing the document's name.
#autosectionlabel_prefix_document = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

autodoc_default_options = {'members':True, 'private-members':True, 'special-members':True}
autodoc_member_order = 'bysource'
