from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='CTDB',
    description='Clustering support for Samba',
    icon='folder-close',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('ctdb'),
    ],
)


def init():
    import main
