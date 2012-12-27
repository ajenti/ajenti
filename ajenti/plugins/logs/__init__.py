from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Logs',
    icon='list',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
