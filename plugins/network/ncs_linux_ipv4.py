from api import *
from ajenti.ui import *

class LinuxIPv4NetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ipv4'
    title = 'IPv4'

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
                    UI.Label(text='Gateway:'),
                    UI.TextInput(name='gateway', value=self.iface['gateway']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Network:'),
                    UI.TextInput(name='network', value=self.iface['network']),
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
                    UI.Label(text='PtP:'),
                    UI.TextInput(name='pointopoint', value=self.iface['pointopoint']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Hardware address:'),
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='MTU:'),
                    UI.TextInput(name='mtu', value=self.iface['mtu']),
                )
            )
        return p

