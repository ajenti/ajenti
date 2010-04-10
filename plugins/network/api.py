from ajenti.com import *
from ajenti.app.api import *

class INetworkConfig(Interface):
    interfaces = None
    nameservers = None

    def save(self):
        pass

    def ns_edit_dialog(self, ns):
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

#TODO: add InterfaceBase class with members that are used from main.py
class Nameserver(object):
    cls = ''
    address = ''
