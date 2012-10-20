from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Dashboard',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import dash
    import api
