from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Nameservers',
    icon='globe',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main
