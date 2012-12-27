from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='File Manager',
    icon='folder-open',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import fm
