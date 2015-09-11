import psutil
import time
from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class UptimeWidget(Widget):
    id = 'uptime'
    name = _('Uptime')
    template = '/dashboard:resources/partial/widgets/uptime.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        return time.time() - psutil.boot_time()
