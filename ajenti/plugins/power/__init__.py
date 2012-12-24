from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Power',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import power
