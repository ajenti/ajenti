from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='S.M.A.R.T.',
    icon='hdd',
    dependencies=[
        PluginDependency('dashboard'),
        BinaryDependency('smartctl')
    ],
)


def init():
    import widget
