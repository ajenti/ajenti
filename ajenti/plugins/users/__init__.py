from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Users',
    icon='group',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
