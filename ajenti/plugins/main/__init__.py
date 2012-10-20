from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import *


info = PluginInfo(
    title='Core',
    dependencies=[
        #PluginDependency('ads')
    ],
)


def init():
    import main
    import api
    import controls_dialogs
