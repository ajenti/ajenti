from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Services',
    icon='play',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import api

    try:
        import dbus
        
        import sm_upstart
        import sm_systemd
    except ImportError:
        pass

    import sm_sysvinit
    import sm_sysvinit_centos
    import sm_freebsd
    import sm_osx

    import main
    import widget
    import sensor
