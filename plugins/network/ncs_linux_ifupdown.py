from ajenti.ui import *

from api import *


class LinuxIfUpDownNetworkConfigSet(NetworkConfigBit):
    cls = 'linux-ifupdown'
    title = 'Scripts'
    autovars = ['up', 'down', 'post-up', 'post-down']
    
    def get_ui(self):
        p = UI.Container(
                UI.Formline(
                    UI.TextInput(name='up', size=40, value=self.iface['up']),
                    text='Pre-up',
                ),
                UI.Formline(
                    UI.TextInput(name='post-up', size=40, value=self.iface['post-up']),
                    text='Post-up',
                ),
                UI.Formline(
                    UI.TextInput(name='down', size=40, value=self.iface['down']),
                    text='Pre-down',
                ),
                UI.Formline(
                    UI.TextInput(name='post-down', size=40, value=self.iface['post-down']),
                    text='Post-down',
                )
            )
        return p
