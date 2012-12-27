from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Resource Manager',
    icon='link',
    dependencies=[
    ],
)


def init():
    import server
