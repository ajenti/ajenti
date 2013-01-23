from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='HDD temperature',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        BinaryDependency('hddtemp')
    ],
)


def init():
    import widget
    import sensor