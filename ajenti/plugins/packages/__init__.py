from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Package manager',
    icon='gift',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main
