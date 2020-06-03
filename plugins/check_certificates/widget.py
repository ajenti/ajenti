from jadi import component
from aj.plugins.dashboard.api import Widget
from datetime import datetime

@component(Widget)
class CertWidget(Widget):
    id = 'cert'
    name = _('Certificates')
    template = '/check_certificates:resources/partial/widget.html'

    def __init__(self, context):
        Widget.__init__(self, context)
        self.last_update = None

    def get_value(self, config):
        now = datetime.now()
        if self.last_update is None:
            self.last_update = now
            return True
        # One update per hour is sufficient for certificates
        if (now-self.last_update).seconds > 3600:
            self.last_update = now
            return True
        return False