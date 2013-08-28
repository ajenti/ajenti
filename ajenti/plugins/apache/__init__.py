from ajenti.api import *
from ajenti.plugins import *
from ajenti.util import platform_select


info = PluginInfo(
    title='Apache',
    icon='globe',
    dependencies=[
        PluginDependency('webserver_common'),
        BinaryDependency(platform_select(
            centos='httpd',
            default='apache2',
        )),
    ],
)


def init():
    import main
