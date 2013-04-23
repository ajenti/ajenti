from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='PostgreSQL',
    icon='table',
    dependencies=[
        PluginDependency('db_common'),
        BinaryDependency('psql'),
    ],
)


def init():
    import main
