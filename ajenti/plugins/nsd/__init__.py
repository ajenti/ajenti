from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='NSD',
    description='NSD DNS server',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('nsd'),
        FileDependency('/etc/nsd3/nsd.conf'),
    ],
)


def init():
    import main
