from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='HDD temperature',
    description='Widget for the hddtemp daemon',
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