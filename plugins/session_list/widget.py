from jadi import component
from aj.plugins.dashboard.api import Widget
from datetime import datetime

@component(Widget)
class SessionWidget(Widget):
    id = 'sessions'
    name = _('Sessions')
    template = '/session_list:resources/partial/widget.html'

    def __init__(self, context):
        Widget.__init__(self, context)
        self.last_update = None

    def get_value(self, config):
        now = datetime.now()
        if self.last_update is None:
            self.last_update = now
            return True
        # One update per 15s is sufficient for sessions
        if (now-self.last_update).seconds > 15:
            self.last_update = now
            return True
        return False