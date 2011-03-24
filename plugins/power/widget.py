from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin

from main import *


class PowerWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Power'
    
    def get_ui(self):
        ui = self.app.inflate('power:widget')
        ui.find('value').set('text', get_uptime())
        return ui
