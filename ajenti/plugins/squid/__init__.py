from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Squid',
    icon='exchange',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('squid3'),
    ],
)


def init():
    import main
