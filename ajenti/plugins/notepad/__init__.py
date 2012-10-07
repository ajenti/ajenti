from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Notepad',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('codemirror'),
    ],
)


def init():
    import notepad
