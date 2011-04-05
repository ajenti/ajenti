from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.core.api import *
from ajenti import apis

from backend import *


class DnsMasqPlugin(apis.services.ServiceControlPlugin):
    text = 'Dnsmasq'
    icon = '/dl/dnsmasq/icon.png'
    folder = 'servers'
    service_name = 'dnsmasq'

    def on_init(self):
        self.backend = Backend(self.app) 
        
    def get_main_ui(self):
        ui = self.app.inflate('dnsmasq:main')
        return ui
   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'progress':
            pass
            
