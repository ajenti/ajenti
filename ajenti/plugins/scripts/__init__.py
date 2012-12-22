from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Scripts',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        PluginDependency('terminal'),
    ],
)


def init():
    import widget
