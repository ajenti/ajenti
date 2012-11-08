from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Sensors',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import hostname
    import uptime
    import load
    import memory
    import cpu
