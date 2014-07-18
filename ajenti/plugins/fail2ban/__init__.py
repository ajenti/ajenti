from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='fail2ban',
    icon='shield',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main