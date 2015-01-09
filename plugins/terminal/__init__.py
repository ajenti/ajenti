from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Terminal',
    icon='console',
    dependencies=[
        PluginDependency('core'),
    ],
    resources=[
        'resources/css/terminal.less',
        
        'resources/js/module.coffee',
        'resources/js/routing.coffee',

        'resources/js/directives/terminal.coffee',
        'resources/js/controllers/index.controller.coffee',
        'resources/js/controllers/view.controller.coffee',
        'resources/js/services/terminals.service.coffee',
    
        'resources/partial/index.html',
        'resources/partial/view.html',
        
        'ng:ajenti.terminal',
    ],
)


def init():
    import main
    import views
