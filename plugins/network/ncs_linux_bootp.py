from ajenti.ui import *

from api import *


class LinuxBootPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-bootp'
    title = 'BootP'
    autovars = ['bootfile', 'server', 'hwaddress']
    
    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.TextInput(name='bootfile', value=self.iface['bootfile']),
                    text='Boot file',
                ),
                UI.Formline(
                    UI.TextInput(name='server', value=self.iface['server']),
                    text='Server',
                ),
                UI.Formline(
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                    text='Hardware address',
                )
            )
        return p
