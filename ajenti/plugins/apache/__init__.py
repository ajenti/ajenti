from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Apache',
    icon='globe',
    dependencies=[
        PluginDependency('webserver_common'),
        BinaryDependency('apache2'),
    ],
)


def init():
    import main
