from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin

from main import *

class PowerWidget(Plugin):
    implements(IDashboardWidget)
    
    def get_ui(self):
        w = UI.Widget(
                UI.Image(file='/dl/power/widget.png'),
                UI.Label(text='Uptime:', bold=True),
                UI.Label(text=get_uptime())
            )
        return w

