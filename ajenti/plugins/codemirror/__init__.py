from ajenti.api import *
from ajenti.plugins import *
from ajenti.ui import *


info = PluginInfo(
    title=_('CodeMirror code editor'),
    description='Adds a rich code editor support to other plugins',
    icon='link',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():

    @p('width', default='auto')
    @p('height', default='auto')
    @p('mode', default='default', type=unicode)
    @p('value', default='', type=unicode, bindtypes=[str, unicode])
    @plugin
    class CodeArea (UIElement):
        typeid = 'codearea'
