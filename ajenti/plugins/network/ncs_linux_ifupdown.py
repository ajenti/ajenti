from ajenti.ui import *
from ajenti.ui.binder import Binder

from api import *


@plugin
class LinuxIfUpDownNetworkConfigSet (NetworkConfigBit):
    cls = 'linux-ifupdown'
    title = 'Scripts'

    def init(self):
        self.append(self.ui.inflate('network:bit-linux-ifupdown'))
        self.binder = Binder(None, self)

    def refresh(self):
        self.binder.setup(self.iface).populate()

    def apply(self):
        self.binder.update()
