from ajenti.ui import *

from api import *


class BSDIPv4NetworkConfigSet(NetworkConfigBit):
    cls = 'bsd-ipv4'
    title = 'IPv4'
    autovars = ['address', 'netmask', 'broadcast', 'metric', 'mtu']
    
    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.TextInput(name='address', value=self.iface['address']),
                    text='Address',
                ),
                UI.Formline(
                    UI.TextInput(name='netmask', value=self.iface['netmask']),
                    text='Network mask',
                ),
                UI.Formline(
                    UI.TextInput(name='broadcast', value=self.iface['broadcast']),
                    text='Broadcast',
                ),
                UI.Formline(
                    UI.TextInput(name='metric', value=self.iface['metric']),
                    text='Routing metric',
                ),
                UI.Formline(
                    UI.TextInput(name='mtu', value=self.iface['mtu']),
                    text='MTU',
                )
            )
        return p
