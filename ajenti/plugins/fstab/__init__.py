from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Filesystems',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import fstab
