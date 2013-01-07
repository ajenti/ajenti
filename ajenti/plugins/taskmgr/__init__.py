from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Processes',
    icon='th-list',
    dependencies=[
        PluginDependency('main'),
        ModuleDependency('psutil'),
    ],
)


def init():
    import main
