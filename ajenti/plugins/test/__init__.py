from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Test',
    icon=None,
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import simple.main
    import events.main
    import notifications.main
    import binder.main
    import http.http
    import classconfig.main
