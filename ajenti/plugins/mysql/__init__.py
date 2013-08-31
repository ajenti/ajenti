from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='MySQL',
    icon='table',
    dependencies=[
        PluginDependency('db_common'),
        BinaryDependency('mysql'),
        BinaryDependency('mysqld'),
    ],
)


def init():
    import main
