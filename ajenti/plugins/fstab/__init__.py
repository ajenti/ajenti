from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Filesystems',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import fstab
    import widget
    import disks