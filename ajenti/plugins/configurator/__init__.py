from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Ajenti Configurator',
    description='Configuration section for setting up Ajenti itself',
    icon='wrench',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import api
    import configurator
