from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Supervisor',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import main
