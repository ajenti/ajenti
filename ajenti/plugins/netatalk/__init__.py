from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Netatalk',
    icon='folder-close',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('afpd'),
    ],
)


def init():
    import main
