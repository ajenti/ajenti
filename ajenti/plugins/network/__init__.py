from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Network',
    icon='exchange',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import widget
    import api
    import main
    import nctp_linux
    import nc_debian
    import nc_centos
    import ncs_linux_basic
    import ncs_linux_ipv4
    import ncs_linux_dhcp
    import ncs_linux_ifupdown
