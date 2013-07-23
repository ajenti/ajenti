from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='BIND9',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('named'),
    ],
)


def init():
    import main
