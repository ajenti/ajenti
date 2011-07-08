from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin

from main import *


class PowerWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Uptime'
    icon = '/dl/power/widget.png'
    name = 'Uptime'
    style = 'linear'
    
    def get_ui(self, cfg, id=None):
        return UI.Label(text=get_uptime())
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, vars):
        pass
                
