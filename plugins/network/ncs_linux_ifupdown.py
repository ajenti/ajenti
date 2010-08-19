from ajenti.ui import *

from api import *


class LinuxIfUpDownNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ifupdown'
    title = 'Scripts'

    def get_ui(self):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Pre-up:'),
                    UI.TextInput(name='up', size=40, value=self.iface['up']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Post-up:'),
                    UI.TextInput(name='post-up', size=40, value=self.iface['post-up']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Pre-down:'),
                    UI.TextInput(name='down', size=40, value=self.iface['down']),
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Post-down:'),
                    UI.TextInput(name='post-down', size=40, value=self.iface['post-down']),
                )
            )
        return p
