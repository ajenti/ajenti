from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='RethinkDB',
    icon='table',
    dependencies=[
        PluginDependency('db_common'),
        BinaryDependency('rethinkdb'),
        ModuleDependency('rethinkdb'),
    ],
)


def init():
    import api
    import main
