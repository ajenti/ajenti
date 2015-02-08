from aj.util import LazyModule
psutil = LazyModule('psutil')

import time

from aj.api import *
from aj.plugins.dashboard.api import Widget


@component(Widget)
class UptimeWidget (Widget):
    id = 'uptime'
    name = 'Uptime'
    template = '/dashboard:resources/partial/widgets/uptime.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        return time.time() - psutil.BOOT_TIME
