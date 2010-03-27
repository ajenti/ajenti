import commands

from ajenti.ui import *
from ajenti import version
from ajenti.app.helpers import CategoryPlugin, ModuleContent, EventProcessor, event
from ajenti.app.session import SessionProxy
from ajenti.utils import shell

class PowerContent(ModuleContent):
    module = 'power'
    path = __file__


class Power(CategoryPlugin):

    text = 'Power'
    description = 'Shudown & reboot'
    icon = '/dl/power/icon.png'

    def on_session_start(self):
        pass
        
    def get_ui(self):
        h = UI.HContainer(
               UI.Image(file='/dl/power/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Power management', size=5),
                   UI.Label(text=('Uptime: ' + get_uptime()))
               )
            )
        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.HContainer(
                    UI.Action(
                        text='Shutdown',
                        id='act-shutdown',
                        icon='/dl/power/shutdown.png',
                        description='Switch off the system'
                    ),
                    UI.Action(
                        text='Reboot',
                        id='act-reboot',
                        icon='/dl/power/reset.png',
                        description='Restart the system'
                    )
                )
            )
        return p


    @event('action/click')
    def on_aclick(self, event, params, vars=None):
        if params[0] == 'act-shutdown':
            shell('notify-send Shutdown')
        if params[0] == 'act-reboot':
            shell('notify-send Reboot')


def get_uptime():
    s = open('/proc/uptime').read().split('.')[0]
    h = s / 3600
    m = s / 60 % 60
    s %= 60
    return str(h) + ':' + ('0' if m < 10 else '') + \
           str(m) + ':' + ('0' if s < 10 else '') + str(s)
               
