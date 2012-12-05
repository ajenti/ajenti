from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Services',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import api
    import sm_upstart
    import sm_sysvinit
    import main
    import widget
