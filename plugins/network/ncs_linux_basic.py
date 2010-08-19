from ajenti.ui import *

from api import *


class LinuxBasicNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-basic'
    title = 'Basic'

    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Auto-enable:'),
                    UI.Checkbox(name='auto', checked=(self.iface.auto)),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Allow hotplug:'),
                    UI.Checkbox(name='hotplug', checked=(self.iface.hotplug)),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Mode:'),
                    UI.Select(
                        UI.SelectOption(text='Loopback', value='loopback', selected=(self.iface.mode=='loopback')),
                        UI.SelectOption(text='Static', value='static', selected=(self.iface.mode=='static')),
                        UI.SelectOption(text='Manual', value='manual', selected=(self.iface.mode=='manual')),
                        UI.SelectOption(text='DHCP', value='dhcp', selected=(self.iface.mode=='dhcp')),
                        UI.SelectOption(text='BootP', value='bootp', selected=(self.iface.mode=='bootp')),
                        UI.SelectOption(text='WVDial', value='wvdial', selected=(self.iface.mode=='wvdial')),
                        UI.SelectOption(text='Zeroconf', value='ipv4ll', selected=(self.iface.mode=='ipv4ll')),
                        name='mode'
                    )
                )
            )
        return p

    def apply(self, vars):
        self.iface.mode = vars.getvalue('mode', '')
        self.iface.auto = (vars.getvalue('auto', 'off') == '1')
        self.iface.hotplug = (vars.getvalue('hotplug', 'off') == '1')
