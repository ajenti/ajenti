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
        if os.path.exists('/proc/loadavg'):
            return [float(open('/proc/loadavg').read().split()[x]) for x in range(3)]
        else:
            tokens = subprocess.check_output(['uptime']).split()
            return [float(x.strip(',')) for x in tokens[-3:]]
