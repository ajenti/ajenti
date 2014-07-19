from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='MongoDB',
    icon='table',
    dependencies=[
        PluginDependency('db_common'),
        BinaryDependency('mongod'),
        ModuleDependency('pymongo'),
    ],
)


def init():
    import api
    import main
