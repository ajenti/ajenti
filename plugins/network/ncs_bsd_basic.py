from ajenti.ui import *

from api import *


class BSDBasicNetworkConfigSet(NetworkConfigBit):
    cls = 'bsd-basic'
    title = 'Basic'

    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Auto-enable:'),
                    UI.Checkbox(name='auto', checked=(self.iface.auto)),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Addressing:'),
                    UI.Select(
                        UI.SelectOption(text='Static', value='static', selected=(self.iface.addressing=='static')),
                        UI.SelectOption(text='DHCP', value='dhcp', selected=(self.iface.addressing=='dhcp')),
                        name='addressing'
                    )
                )
            )
        return p

    def apply(self, vars):
        self.iface.addressing = vars.getvalue('addressing', '')
        self.iface.auto = (vars.getvalue('auto', 'off') == '1')
