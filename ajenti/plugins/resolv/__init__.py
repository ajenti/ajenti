from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Nameservers',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import resolv
