# -*- coding: utf-8 -*-
#
# pyZacros documentation build configuration file

from datetime import date

# ==================================================================================
# If we build from the userdoc, we should use the configuration from global_conf.py,
# otherwise we should define a fall-back config for the stand-alone doc.
# ==================================================================================

if tags.has('scm_theme'):

    from global_conf import *
    project, htmlhelp_basename, latex_documents = set_project_specific_var ('pyZacros')
    # html_logo = '_static/pyZacros_logo_compact.svg'

else:
    extensions = []
    templates_path = ['_templates']
    source_suffix = '.rst'
    master_doc = 'index'
    project = u'pyZacros'
    copyright = u'%i, Software for Chemistry & Materials'%(date.today().year)
    exclude_patterns = []
    add_function_parentheses = True
    html_theme = 'nature'
    html_title = 'pyZacros documentation'
    html_favicon = '_static/favicon.ico'
    html_static_path = ['_static']
    html_show_sourcelink = False
    html_show_sphinx = False
    htmlhelp_basename = 'pyZacrosdoc'


extensions += [
    'sphinx.ext.autodoc',
]


# Avoid duplicate names by prefixing the document's name.
#autosectionlabel_prefix_document = True

# Enable display of '.. todo::' directives in build:
todo_include_todos = True
# And emit warnings when building the docs for todos:
todo_emit_warnings = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python3': ('http://docs.python.org/3.6', None)}

autodoc_default_flags = ['members', 'private-members', 'special-members']
autodoc_member_order = 'bysource'


# # Probably not needed, but syntax highlighting didnt seem to work
# rst_prolog = """
# .. role:: pycode(code)
#     :language: python
# """
