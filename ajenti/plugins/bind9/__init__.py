from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='BIND9',
    description='BIND9 DNS server',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('named'),
    ],
)


def init():
    import main
