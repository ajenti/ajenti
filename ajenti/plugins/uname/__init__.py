from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='uname widget',
    icon='cog',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import widget
