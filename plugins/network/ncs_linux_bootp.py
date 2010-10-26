from ajenti.ui import *

from api import *


class LinuxBootPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-bootp'
    title = 'BootP'
    autovars = ['bootfile', 'server', 'hwaddress']
    
    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Boot file:'),
                    UI.TextInput(name='bootfile', value=self.iface['bootfile']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Server:'),
                    UI.TextInput(name='server', value=self.iface['server']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Hardware address:'),
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                )
            )
        return p
