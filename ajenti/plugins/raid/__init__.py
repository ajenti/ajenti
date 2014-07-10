from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='RAID',
    description='mdadm status display',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        BinaryDependency('mdadm'),
        FileDependency('/proc/mdstat'),
    ],
)


def init():
    import api
    import main
