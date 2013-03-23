from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='ajenti.org integration',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
