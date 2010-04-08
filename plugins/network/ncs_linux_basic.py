from api import *
from ajenti.ui import *

class LinuxBasicNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-basic'

    def get_ui(self):
        return UI.Label(text='Basic', size=3)

