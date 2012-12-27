from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Services',
    icon='play',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        ModuleDependency('lolz'),
    ],
)


def init():
    import api
    import sm_upstart
    import sm_sysvinit
    import main
    import widget
