from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin

from main import *


class PowerWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Uptime'
    
    def get_ui(self):
        w = UI.HContainer(
                    UI.Image(file='/dl/power/widget.png'),
                    UI.Label(text='System uptime:', bold=True),
                    UI.Label(text=get_uptime())
            )
        return w
