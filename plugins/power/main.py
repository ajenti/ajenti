import re
import os

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
    minute = 60
    hour = minute * 60
    day = hour * 24

    d = h = m = 0

    try:
        s = int(open('/proc/uptime').read().split('.')[0])

        d = s / day
        s -= d * day
        h = s / hour
        s -= h * hour
        m = s / minute
        s -= m * minute
    except IOError:
        # Try use 'uptime' command
        up = os.popen('uptime').read()
        if up:
            uptime = re.search('up\s+(.*?),\s+[0-9]+ user',up).group(1)
            return uptime

    uptime = ""
    if d > 1:
        uptime = "%d days, "%d
    elif d == 1:
        uptime = "1 day, "

    return uptime + "%d:%02d:%02d"%(h,m,s)
               
