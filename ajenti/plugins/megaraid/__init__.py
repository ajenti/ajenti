from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='RAID',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import api
    import main
