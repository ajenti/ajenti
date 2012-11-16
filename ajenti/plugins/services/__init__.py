from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Services',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import api
    import sm_upstart
    import main
