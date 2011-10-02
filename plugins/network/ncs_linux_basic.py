from ajenti.ui import *

from api import *


class LinuxBasicNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-basic'
    title = 'Basic'

    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.Checkbox(name='auto', checked=(self.iface.auto)),
                    text='Auto-enable',
                ),
                UI.Formline(
                    UI.SelectInput(
                        UI.SelectOption(text='Loopback', value='loopback', selected=(self.iface.addressing=='loopback')),
                        UI.SelectOption(text='Static', value='static', selected=(self.iface.addressing=='static')),
                        UI.SelectOption(text='Manual', value='manual', selected=(self.iface.addressing=='manual')),
                        UI.SelectOption(text='DHCP', value='dhcp', selected=(self.iface.addressing=='dhcp')),
                        UI.SelectOption(text='BootP', value='bootp', selected=(self.iface.addressing=='bootp')),
                        UI.SelectOption(text='WVDial', value='wvdial', selected=(self.iface.addressing=='wvdial')),
                        UI.SelectOption(text='Zeroconf', value='ipv4ll', selected=(self.iface.addressing=='ipv4ll')),
                        name='addressing'
                    ),
                    text='Addressing',
                )
            )
        return p

    def apply(self, vars):
        self.iface.addressing = vars.getvalue('addressing', '')
        self.iface.auto = (vars.getvalue('auto', 'off') == '1')
