from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NTPd control',
    icon='time',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('ntpd'),
    ],
)


def init():
    import main
