from ajenti.api import *
from ajenti.plugins import *
from ajenti.util import platform_select


info = PluginInfo(
    title='Apache',
    description='Apache 2 web server',
    icon='globe',
    dependencies=[
        PluginDependency('webserver_common'),
        BinaryDependency(platform_select(
            mageia='httpd',
            centos='httpd',
            freebsd='apachectl',
            default='apache2',
        )),
    ],
)


def init():
    import main
