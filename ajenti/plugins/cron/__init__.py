from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Cron',
    icon='time',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
