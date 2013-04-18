from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Ajenti Configurator',
    icon='wrench',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import api
    import configurator
