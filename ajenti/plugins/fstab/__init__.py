from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Filesystems',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        FileDependency('/etc/fstab'),
    ],
)


def init():
    import main
    import widget
    import disks
    import iops