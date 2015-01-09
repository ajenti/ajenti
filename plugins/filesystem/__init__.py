from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Filesystem API',
    icon='cog',
    dependencies=[
        PluginDependency('core'),
    ],
    resources=[
        'resources/js/module.coffee',

        'resources/js/directives/fileDialog.coffee',
        'resources/js/services/filesystem.service.coffee',
    
        'ng:util.filesystem',
    ],
)


def init():
    import views
