from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='DHCP Server',
    icon='sitemap',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('dhcpd'),
    ],
)


def init():
    import main
