from ajenti.ui import *
from ajenti.ui.binder import Binder

from api import *


@plugin
class LinuxIPv4NetworkConfigSet (NetworkConfigBit):
    cls = 'linux-ipv4'
    title = 'IPv4'

    def init(self):
        self.append(self.ui.inflate('network:bit-linux-ipv4'))
        self.binder = Binder(None, self)

    def refresh(self):
        self.binder.setup(self.iface).populate()

    def apply(self):
        self.binder.update()
