from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Hosts',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import hosts
