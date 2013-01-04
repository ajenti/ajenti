from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Supervisor',
    icon='play',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('supervisord'),
    ],
)


def init():
    import main
