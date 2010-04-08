from api import *
from ajenti.ui import *

class LinuxIfUpDownNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ifupdown'

    def get_ui(self):
        return UI.Label(text='Scripts', size=3)
