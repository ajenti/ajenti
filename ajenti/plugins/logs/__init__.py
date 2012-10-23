from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Logs',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
