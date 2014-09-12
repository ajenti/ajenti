from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Hosts',
    icon='sitemap',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
