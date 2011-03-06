from ajenti.ui import *
from ajenti import version
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell

from backend import *


class PowerPlugin(CategoryPlugin):
    text = 'Power'
    icon = '/dl/power/icon.png'
    folder = 'hardware'

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=('Uptime: ' + get_uptime())), title='Power Management', icon='/dl/power/icon.png')

        els = UI.VContainer()
        for ac in get_ac_adapters():
            img = 'present' if ac.present else 'none'
            st = 'Active' if ac.present else 'Offline'
            els.append(UI.ElementBox(UI.HContainer(
                          UI.Image(file='/dl/power/ac-%s.png'%img),
                          UI.VContainer(
                              UI.Label(text='AC Adapter %s' % ac.name, size=2),
                              UI.Label(text=st)
                          )
                      )))

        for bat in get_batteries():
            if bat.present:
                img = str(int((bat.charge+19)/20)*20)
            else:
                img = '0'
            st = 'Active' if bat.present else 'Offline'
            if bat.present:
                st += ' - %i%%' % bat.charge

            els.append(UI.ElementBox(UI.HContainer(
                          UI.Image(file='/dl/power/battery-%s.png'%img),
                          UI.VContainer(
                              UI.Label(text='Battery %s' % bat.name, size=2),
                              UI.Label(text=st)
                          )
                      )))

        c = UI.VContainer(
                UI.HContainer(
                    UI.WarningButton(text='Shutdown', id='shutdown', msg='Shutdown machine'),
                    UI.WarningButton(text='Reboot', id='reboot', msg='Reboot machine')
                ),
                els,
                spacing=20
            )
        panel.append(c)
        return panel


    @event('button/click')
    def on_aclick(self, event, params, vars=None):
        if params[0] == 'shutdown':
            shell('shuwdown -p now')
        if params[0] == 'reboot':
            shell('reboot')
