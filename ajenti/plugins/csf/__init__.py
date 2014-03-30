from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='CSF Firewall',
    icon='fire',
    dependencies=[
        BinaryDependency('csf'),
        PluginDependency('main'),
    ],
)


def init():
    import main
