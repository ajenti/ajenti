from ajenti.com import *
from ajenti.app.api import *


class INetworkConfig(Interface):
    interfaces = None
    
    def save(self):
        pass

"""
    def up(self, iface):
        pass

    def down(self, iface):
        pass

    def get_ui_info(self, iface):
        pass
        
    def get_tx(self, iface):
        pass

    def get_rx(self, iface):
        pass

    def get_ip(self, iface):
        pass

    def detect_dev_class(self, iface):
        pass

"""        
    
class INetworkConfigBit(Interface):
    def get_ui(self):
        pass

    def apply(self, vars):
        pass


class NetworkConfigBit(Plugin):
    implements(INetworkConfigBit)
    multi_instance = True

    cls = 'unknown'
    iface = None
    title = 'Unknown'

    autovars = []
    
    def __init__(self):
        self.params = {}

    def get_ui(self):
        pass

    def apply(self, vars):
        for k in self.autovars:
            if vars.getvalue(k, None) is not None:
                self.iface[k] = vars.getvalue(k, '')
                if self.iface[k] == '':
                    del self.iface.params[k]


class NetworkInterface(object):
    def __init__(self):
        self.up = False
        self.auto = False
        self.name = ''
        self.devclass = ''
        self.bits = []
        self.params = {}
        self.type = ''
        
    def __getitem__(self, idx):
        if self.params.has_key(idx):
            return self.params[idx]
        else:
            return ''

    def __setitem__(self, idx, val):
        self.params[idx] = val
        