from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='File Manager',
    icon='folder-open',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('tasks'),
    ],
)


def init():
    import fm
