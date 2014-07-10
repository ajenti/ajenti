from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Firewall',
    description='Linux iptables firewall',
    icon='fire',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main
