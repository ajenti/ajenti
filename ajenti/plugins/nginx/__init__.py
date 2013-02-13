from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NGINX',
    icon='globe',
    dependencies=[
        PluginDependency('webserver_common'),
        BinaryDependency('nginx'),
    ],
)


def init():
    import main
