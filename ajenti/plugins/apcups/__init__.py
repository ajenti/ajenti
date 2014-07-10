from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='APC UPS Status',
    description='APC UPS monitoring daemon',
    icon='bolt',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
        BinaryDependency('apcaccess'),
    ],
)


def init():
    import widget
