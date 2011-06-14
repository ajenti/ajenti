from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin

from main import *


class PowerWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Uptime'
    icon = '/dl/power/icon.png'
    name = 'Uptime'
    
    def get_ui(self, cfg):
        ui = self.app.inflate('power:widget')
        ui.find('value').set('text', get_uptime())
        return ui
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, event, params, vars):
        pass
                
