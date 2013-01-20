from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Munin',
    icon='stethoscope',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import main
    