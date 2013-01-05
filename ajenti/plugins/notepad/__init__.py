from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Notepad',
    icon='edit',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('codemirror'),
    ],
)


def init():
    import notepad
