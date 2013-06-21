from ajenti.api import plugin
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.ui import UIElement


@plugin
class DashboardWelcome (UIElement):
    typeid = 'dashboard:welcome'


@plugin
class WelcomeWidget (DashboardWidget):
    name = _('Welcome')
    icon = 'comment'

    def init(self):
        self.append(self.ui.inflate('dashboard:welcome'))
