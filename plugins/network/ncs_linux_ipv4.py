from api import *
from ajenti.ui import *

class LinuxIPv4NetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ipv4'

    def get_ui(self):
        return UI.Label(text='IPv4', size=3)
