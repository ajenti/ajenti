from ajenti.com import *
from ajenti.app.api import *

class INetworkConfig(Interface):
    interfaces = None

    def save(self):
        pass


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

    def __init__(self):
        self.params = {}

    def get_ui(self):
        pass

    def apply(self, vars):
        for k in vars:
            if vars.getvalue(k, '') != '':
                self.iface[k] = vars.getvalue(k, '')
