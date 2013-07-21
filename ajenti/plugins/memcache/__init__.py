from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Memcache',
    icon='cog',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        BinaryDependency('memcached'),
    ],
)


def init():
    import widget
