from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='needrestart',
    description='Show pending service/container restart and system reboot',
    icon='restart',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        PluginDependency('power'),
        BinaryDependency('needrestart'),
    ],
)


def init():
    import widget
