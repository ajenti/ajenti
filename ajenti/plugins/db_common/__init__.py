from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Database Commons',
    icon='table',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import api
