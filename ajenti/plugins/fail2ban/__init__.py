from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='fail2ban',
    icon='shield',
    dependencies=[
        PluginDependency('main'),
        BinaryDependency('fail2ban-client'),
        BinaryDependency('fail2ban-regex'),
    ],
)


def init():
    import main