from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Nameservers',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        FileDependency('/etc/resolv.conf'),
    ],
)


def init():
    import main
