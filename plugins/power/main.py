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
        ui = self.app.inflate('power:main')
        
        els = ui.find('list')
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

        return ui


    @event('button/click')
    def on_aclick(self, event, params, vars=None):
        if params[0] == 'shutdown':
            shell('shuwdown -p now')
        if params[0] == 'reboot':
            shell('reboot')
