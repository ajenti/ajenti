from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NGINX',
    dependencies=[
        PluginDependency('webserver_common'),
    ],
)


def init():
    import main
