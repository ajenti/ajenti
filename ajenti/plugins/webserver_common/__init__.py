from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Webserver Commons',
    icon='cogs',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import api
