from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Supervisor',
    icon='play',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import main
