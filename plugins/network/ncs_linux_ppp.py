from api import *
from ajenti.ui import *

class LinuxBootPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ppp'
    title = 'PPP'

    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Provider:'),
                    UI.TextInput(name='provider', value=self.iface['provider']),
                )
            )
        return p
