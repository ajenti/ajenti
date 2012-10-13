from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Terminal',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
