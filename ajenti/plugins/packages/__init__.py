from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Package manager',
    icon='gift',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('terminal')
    ],
)


def init():
    import main
    import pm_apt
    import pm_bsd
    import pm_yum
    import pm_pacman
    import pm_urpmi
    import pm_macports
    import installer