from ajenti.ui import *

from api import *


class LinuxDHCPNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-dhcp'
    title = 'DHCP'
    autovars = ['hostname', 'leasehours', 'leasetime', 'vendor', 'client', 'hwaddress']
    
    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.TextInput(name='hostname', value=self.iface['hostname']),
                    text='Hostname',
                ),
                UI.Formline(
                    UI.TextInput(name='leasehours', value=self.iface['leasehours']),
                    text='Lease hours',
                ),
                UI.Formline(
                    UI.TextInput(name='leasetime', value=self.iface['leasetime']),
                    text='Lease time',
                ),
                UI.Formline(
                    UI.TextInput(name='vendor', value=self.iface['vendor']),
                    text='Vendor ID',
                ),
                UI.Formline(
                    UI.TextInput(name='client', value=self.iface['client']),
                    text='Client ID',
                ),
                UI.Formline(
                    UI.TextInput(name='hwaddress', value=self.iface['hwaddress']),
                    text='Hardware address',
                )
            )
        return p
