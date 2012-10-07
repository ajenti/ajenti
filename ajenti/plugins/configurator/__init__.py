from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Configuration',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import configurator
