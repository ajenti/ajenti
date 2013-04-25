from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NFS Exports',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        BinaryDependency('nfsstat')
    ],
)


def init():
    import main
