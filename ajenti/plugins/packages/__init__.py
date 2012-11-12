from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Package manager',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main
