from ajenti.ui import *

from api import *


class LinuxDHCPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-dhcp'
    title = 'DHCP'

    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Hostname:'),
                    UI.TextInput(name='hostname', value=self.iface['hostname']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Lease hours:'),
                    UI.TextInput(name='leasehours', value=self.iface['leasehours']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Lease time:'),
                    UI.TextInput(name='leasetime', value=self.iface['leasetime']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Vendor ID:'),
                    UI.TextInput(name='vendor', value=self.iface['vendor']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Client ID:'),
                    UI.TextInput(name='client', value=self.iface['client']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Hardware address:'),
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                )
            )
        return p
