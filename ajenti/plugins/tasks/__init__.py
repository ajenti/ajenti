from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Tasks',
    icon='cog',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('cron'),
    ],
)


def init():
    import api
    import manager
    import main
    import tasks
