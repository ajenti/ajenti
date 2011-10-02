from ajenti.ui import *

from api import *


class LinuxIPv4NetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ipv4'
    title = 'IPv4'
    autovars = ['address', 'netmask', 'gateway', 'network', 'broadcast', 'metric', 'pointopoint', 'hwaddress', 'mtu']
    
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
                    UI.TextInput(name='gateway', value=self.iface['gateway']),
                    text='Gateway',
                ),
                UI.Formline(
                    UI.TextInput(name='network', value=self.iface['network']),
                    text='Network',
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
                    UI.TextInput(name='pointopoint', value=self.iface['pointopoint']),
                    text='PtP',
                ),
                UI.Formline(
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                    text='Hardware address',
                ),
                UI.Formline(
                    UI.TextInput(name='mtu', value=self.iface['mtu']),
                    text='MTU',
                )
            )
        return p
