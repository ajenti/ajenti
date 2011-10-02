from ajenti.ui import *

from api import *


class LinuxBootPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ppp'
    title = 'PPP'
    autovars = ['provider']
    
    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.TextInput(name='provider', value=self.iface['provider']),
                    text='Provider',
                )
            )
        return p
