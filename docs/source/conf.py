# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.ifconfig', 'sphinx.ext.viewcode']  # 'sphinx.ext.intersphinx']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Ajenti'
copyright = u'2013, Eugene Pankov'

import ajenti
version = ajenti.__version__
release = ajenti.__version__

exclude_patterns = []
add_function_parentheses = True

pygments_style = 'sphinx'


# ReadTheDocs
import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    
html_static_path = ['_static']
htmlhelp_basename = 'Ajentidoc'


# Gettext
import gettext
translation = gettext.NullTranslations()
translation.install(unicode=True)  



intersphinx_mapping = {'http://docs.python.org/': None}


def skip(app, what, name, obj, skip, options):
    if hasattr(obj, '_plugin'):
        for x in ['get', 'new', 'classname']:
            if hasattr(obj, x):
                try:
                    delattr(obj, x)
                except:
                    pass
    if hasattr(obj, '_interface'):
        for x in ['get', 'get_all', 'get_instances', 'get_class', 'get_classes']:
            if hasattr(obj, x):
                try:
                    delattr(obj, x)
                except:
                    pass
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
