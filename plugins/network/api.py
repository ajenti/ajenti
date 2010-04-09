from ajenti.com import *
from ajenti.app.api import *

class INetworkConfig(Interface):
    interfaces = None

    def get_text(self):
        pass


class INetworkConfigBit(Interface):
    def get_ui(self):
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
