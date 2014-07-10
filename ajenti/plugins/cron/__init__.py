from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Cron',
    description='Cron task scheduler',
    icon='time',
    dependencies=[
        PluginDependency('main'),
        BinaryDependency('crontab'),
    ],
)


def init():
    import main
