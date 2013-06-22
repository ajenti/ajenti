from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Network',
    icon='exchange',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import widget
    import api
