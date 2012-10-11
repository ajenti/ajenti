from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='File Manager',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import fm
