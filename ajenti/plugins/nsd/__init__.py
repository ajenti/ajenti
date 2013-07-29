from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NSD',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('nsd'),
    ],
)


def init():
    import main
