import psutil

from ajenti.api import *
from ajenti.ui import *


@plugin
class NetworkManager (BasePlugin):
    def get_devices(self):
        return psutil.network_io_counters(pernic=True).keys()


@interface
class INetworkConfig (object):
    interfaces = {}

    @property
    def interface_list(self):
        return self.interfaces.values()

    def rescan(self):
        pass

    def save(self):
        pass


@interface
class INetworkConfigBit (object):
    def apply(self):
        pass


@plugin
class NetworkConfigBit (UIElement, INetworkConfigBit):
    cls = 'unknown'
    iface = None
    title = 'Unknown'
    typeid = 'box'


class NetworkInterface(object):
    def __init__(self):
        self.up = False
        self.auto = False
        self.name = ''
        self.devclass = ''
        self.addressing = 'static'
        self.bits = []
        self.params = {'address': '0.0.0.0'}
        self.type = ''
        self.editable = True

    def __getitem__(self, idx):
        if idx in self.params:
            return self.params[idx]
        else:
            return ''

    def __setitem__(self, idx, val):
        self.params[idx] = val

    def add_bits(self, ui):
        for cls in INetworkConfigBit.get_classes():
            if cls.cls in self.bit_classes:
                b = cls.new(ui)
                b.iface = self
                b.refresh()
                self.bits.append(b)
