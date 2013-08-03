from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='OpenVPN',
    icon='globe',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('openvpn'),
    ],
)


def init():
    import backend
    import main
