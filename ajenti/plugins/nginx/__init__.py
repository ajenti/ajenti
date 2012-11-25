from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NGINX',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import configurator
