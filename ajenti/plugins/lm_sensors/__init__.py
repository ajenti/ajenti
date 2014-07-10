from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='LM-Sensors',
    description='lm-sensors temperature sensor widgets',
    icon='leaf',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        BinaryDependency('sensors'),
    ],
)


def init():
    import main
