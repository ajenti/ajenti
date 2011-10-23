from ajenti.ui import *
from ajenti.utils import *
from ajenti import apis
from ajenti.com import implements, Plugin
from api import *

        
class NetworkWidget(Plugin):
    implements(apis.dashboard.IWidget)
    icon = '/dl/network/down.png'
    name = 'Network monitor'
    title = None
    style = 'normal'

    def __init__(self):
        self.iface = None
        
    def get_ui(self, cfg, id=None):
        self.iface = cfg
        self.title = 'Network interface: %s' % cfg
        be = self.app.get_backend(INetworkConfig)
        if not cfg in be.interfaces:
            return UI.Label(text='Interface not found')
        i = be.interfaces[cfg]
        self.icon = '/dl/network/%s.png'%('up' if i.up else 'down')
        
        ui = self.app.inflate('network:widget')
        ui.find('ip').set('text', be.get_ip(i))
        ui.find('in').set('text', str_fsize(be.get_rx(i)))
        ui.find('out').set('text', str_fsize(be.get_tx(i)))
        return ui
                
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        be = self.app.get_backend(INetworkConfig)
        dlg = self.app.inflate('network:widget-config')
        for i in be.interfaces:
            dlg.append('list', UI.Radio(
                value=i,
                text=i,
                name='iface'
            ))
        return dlg
        
    def process_config(self, vars):
        return vars.getvalue('iface', None)
