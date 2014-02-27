from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='HDD state',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        BinaryDependency('hdparm')
    ],
)


def init():
    import widget
