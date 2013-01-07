from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='LM-Sensors',
    icon='leaf',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import main
