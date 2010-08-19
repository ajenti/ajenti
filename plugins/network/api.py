from ajenti.com import *
from ajenti.app.api import *


class INetworkConfig(Interface):
    interfaces = None
    nameservers = None

    def save(self):
        pass

    def ns_edit_dialog(self, ns):
        pass

    def new_iface(self):
        pass

    def new_nameserver(self):
        pass

    def up(self, iface):
        pass

    def down(self, iface):
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


class NetworkInterfaceBase(object):
    clsname = ''
    up = False
    addr = ''
    name = 'unknown'
    bits = None

    def __init__(self):
        self.bits = []


class NameserverBase(object):
    cls = ''
    address = ''
