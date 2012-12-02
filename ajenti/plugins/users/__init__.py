from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Users',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
