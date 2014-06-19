from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='SNMPd control',
    icon='exchange',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('snmpd'),
    ],
)


def init():
    import main
