import multiprocessing
import os
import subprocess
from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class LoadAverageWidget(Widget):
    id = 'loadavg'
    name = _('Load average')
    template = '/dashboard:resources/partial/widgets/loadavg.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        k = 1.0
        if config and config.get('divide', False):
            k /= multiprocessing.cpu_count()
        if os.path.exists('/proc/loadavg'):
            return [float(open('/proc/loadavg').read().split()[x]) * k for x in range(3)]

        tokens = subprocess.check_output(['uptime']).decode().split()
        return [float(x.strip(',').replace(',', '.')) * k for x in tokens[-3:]]
