from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Notepad',
    icon='pencil',
    dependencies=[
        PluginDependency('core'),
        PluginDependency('ace'),
        PluginDependency('filesystem'),
    ],
    resources=[
        'resources/js/module.coffee',
        'resources/js/routing.coffee',

        'resources/js/controllers/index.controller.coffee',
    
        'resources/partial/index.html',
        
        'ng:ajenti.notepad',
    ],
)


def init():
    import main
