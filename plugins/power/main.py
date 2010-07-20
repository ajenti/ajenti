import re
import os

from ajenti.ui import *
from ajenti import version
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import CategoryPlugin, ModuleContent, EventProcessor, event
from ajenti.app.session import SessionProxy
from ajenti.utils import shell

class PowerContent(ModuleContent):
    module = 'power'
    path = __file__


class PowerPlugin(CategoryPlugin):

    implements((ICategoryProvider, 90))

    text = 'Power'
    icon = '/dl/power/icon.png'

    def on_session_start(self):
        pass
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=('Uptime: ' + get_uptime())), title='Power Management', icon='/dl/power/icon.png')
        c = UI.VContainer(
                UI.ErrorBox(title='Dangerous area', text='These actions cannot be cancelled. Be careful when using them remotely.'),
                UI.Spacer(height=20),
                UI.HContainer(
                    UI.WarningButton(text='Shutdown', id='shutdown'),
                    UI.WarningButton(text='Reboot', id='reboot')
                )
            )
        panel.appendChild(c)
        return panel


    @event('button/click')
    def on_aclick(self, event, params, vars=None):
        if params[0] == 'shutdown':
            shell('poweroff')
        if params[0] == 'reboot':
            shell('reboot')


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
               
