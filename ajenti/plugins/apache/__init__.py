from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Apache',
    icon='globe',
    dependencies=[
        PluginDependency('webserver_common'),
    ],
)


def init():
    import main
