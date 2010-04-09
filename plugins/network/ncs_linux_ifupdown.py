from api import *
from ajenti.ui import *

class LinuxIfUpDownNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ifupdown'
    title = 'Scripts'

    def get_ui(self):
        return UI.Label(text='Scripts', size=3)
