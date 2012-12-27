from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Plugins',
    icon='cogs',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import plugins
