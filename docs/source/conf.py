# -*- coding: utf-8 -*-
import sys
import os
import datetime

sys.path.insert(0, os.path.abspath('../../ajenti-core'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.ifconfig', 'sphinx.ext.viewcode']  # 'sphinx.ext.intersphinx']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'Ajenti'
copyright = f'{datetime.datetime.now().year}, Eugene Pankov'

import aj
version = aj.__version__
release = aj.__version__


exclude_patterns = []
add_function_parentheses = True

pygments_style = 'sphinx'


# ReadTheDocs
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']
htmlhelp_basename = 'Ajentidoc'


html_context = {
    "disqus_shortname": 'ajenti',
    "github_base_account": 'Eugeny',
    "github_project": 'ajenti',
}

# Gettext
import gettext
translation = gettext.NullTranslations()
translation.install()


intersphinx_mapping = {'http://docs.python.org/': None}


def skip(app, what, name, obj, skip, options):
    for x in ['all', 'any', 'classes', 'implementations']:
        if hasattr(obj, x):
            try:
                delattr(obj, x)
            except:
                pass
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)




USE_PIP_INSTALL = True

class Mock():
    __all__ = []

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'

        if name[0] == name[0].upper():
            mockType = type(name, (), {})
            mockType.__module__ = __name__
            return mockType

        return Mock()

MOCK_MODULES = [
    'augeas',
    'gevent',
    'gevent-socketio-hartwork',
    'gevent.event',
    'gevent.lock',
    'gevent.pywsgi',
    'gevent.queue',
    'gevent.socket',
    'gevent.ssl',
    'gevent.timeout',
    'gipc',
    'greenlet',
    'lxml',
    'lxml.etree',
    'lxml.html',
    'pexpect',
    'Pillow',
    'psutil',
    'pyOpenSSL',
    'python-ldap',
    'supervisor',
    'supervisor.options',
    'scrypt',
    'setproctitle',
    'socketio',
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()




import aj.api
import aj.config
import aj.core
import aj.log
import aj.plugins

aj.context = aj.api.Context()
aj.init()
aj.plugins.PluginManager.get(aj.context).load_all_from([aj.plugins.DirectoryPluginProvider('../../plugins-new')])
