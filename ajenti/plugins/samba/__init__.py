from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Samba',
    icon='folder-close',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('smbd'),
    ],
)


def init():
    import main
