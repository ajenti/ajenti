from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='CTDB',
    icon='folder-close',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('ctdb'),
    ],
)


def init():
    import main
