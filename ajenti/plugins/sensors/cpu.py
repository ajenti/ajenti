import psutil

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget


@plugin
class CPUSensor (Sensor):
    id = 'cpu'
    timeout = 3

    def measure(self, variant=None):
        return [x / 100 for x in psutil.cpu_percent(interval=0, percpu=True)]


@plugin
class CPUWidget (DashboardWidget):
    name = _('CPU usage')
    icon = 'signal'

    def init(self):
        self.sensor = Sensor.find('cpu')
        self.append(self.ui.inflate('sensors:cpu-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = _('CPU usage')
        for value in self.sensor.value():
            l = self.ui.inflate('sensors:cpu-line')
            l.find('progress').value = value
            l.find('value').text = '%i%%' % int(value * 100)
            self.find('lines').append(l)
