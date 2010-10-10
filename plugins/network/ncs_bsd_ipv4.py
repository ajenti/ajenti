from ajenti.ui import *

from api import *


class BSDIPv4NetworkConfigSet(NetworkConfigBit):
    cls = 'bsd-ipv4'
    title = 'IPv4'
    autovars = ['address', 'netmask', 'broadcast', 'metric', 'mtu']
    
    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Address:'),
                    UI.TextInput(name='address', value=self.iface['address']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Network mask:'),
                    UI.TextInput(name='netmask', value=self.iface['netmask']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Broadcast:'),
                    UI.TextInput(name='broadcast', value=self.iface['broadcast']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Routing metric:'),
                    UI.TextInput(name='metric', value=self.iface['metric']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='MTU:'),
                    UI.TextInput(name='mtu', value=self.iface['mtu']),
                )
            )
        return p
