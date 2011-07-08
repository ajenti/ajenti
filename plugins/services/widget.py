from ajenti.ui import *
from ajenti.utils import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from api import *

        
class ServiceWidget(Plugin):
    implements(IDashboardWidget)
    icon = '/dl/network/down.png'
    name = 'Service control'
    title = None
    style = 'linear'

    def __init__(self):
        self.iface = None
        
    def get_ui(self, cfg, id=None):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        running = mgr.get_status(cfg) == 'running'
        self.title = cfg
        self.icon = '/dl/core/ui/stock/service-' + ('run.png' if running else 'stop.png')
        
        ui = self.app.inflate('services:widget')
        if running:
            ui.remove('start')
            ui.find('stop').set('id', id+'/stop')
            ui.find('restart').set('id', id+'/restart')
        else:
            ui.remove('stop')
            ui.remove('restart')
            ui.find('start').set('id', id+'/start')
        return ui
                
    def handle(self, event, params, cfg, vars=None):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        if params[0] == 'start':
            mgr.start(cfg)
        if params[0] == 'stop':
            mgr.stop(cfg)
        if params[0] == 'restart':
            mgr.restart(cfg)
    
    def get_config_dialog(self):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        dlg = self.app.inflate('services:widget-config')
        for s in sorted(mgr.list_all()):
            dlg.append('list', UI.SelectOption(
                value=s.name,
                text=s.name,
            ))
        return dlg
        
    def process_config(self, vars):
        return vars.getvalue('svc', None)
