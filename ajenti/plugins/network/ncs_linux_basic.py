from ajenti.ui import *
from ajenti.ui.binder import Binder

from api import *


@plugin
class LinuxBasicNetworkConfigSet (NetworkConfigBit):
    cls = 'linux-basic'
    title = 'Basic'

    def init(self):
        self.append(self.ui.inflate('network:bit-linux-basic'))
        self.binder = Binder(self.iface, self)

    def refresh(self):
        self.binder.reset(self.iface).autodiscover().populate()

    def apply(self):
        self.binder.update()
