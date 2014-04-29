from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import *


info = PluginInfo(
    title='Core',
    icon='link',
    dependencies=[
    ],
)


def init():
    import main
    import api
    import passwd
    import controls_binding
    import controls_containers
    import controls_simple
    import controls_inputs
    import controls_dialogs
