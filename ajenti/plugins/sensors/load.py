import subprocess

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget


class BaseLoadSensor (Sensor):
    id = 'load'
    timeout = 1

    def get_variants(self):
        return ['1 min', '5 min', '15 min']


@plugin
class LinuxLoadSensor (BaseLoadSensor):
    platforms = ['debian', 'centos']

    def measure(self, variant):
        idx = self.get_variants().index(variant)
        return float(open('/proc/loadavg').read().split()[idx])


@plugin
class BSDLoadSensor (BaseLoadSensor):
    platforms = ['freebsd']

    def measure(self, variant):
        idx = self.get_variants().index(variant)
        tokens = subprocess.check_output(['uptime']).split()
        loads = [float(x.strip(',')) for x in tokens[-3:]]
        return loads[idx]


@plugin
class LoadWidget (DashboardWidget):
    name = _('Load average')
    icon = 'signal'

    def init(self):
        self.sensor = Sensor.find('load')
        self.append(self.ui.inflate('sensors:value-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = _('Load average')
        self.find('value').text = '&nbsp;&nbsp;'.join(str(self.sensor.value(x)) for x in self.sensor.get_variants())
