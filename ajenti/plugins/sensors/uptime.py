from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_timedelta


@plugin
class UptimeSensor (Sensor):
    id = 'uptime'
    timeout = 1

    def measure(self, device):
        return float(open('/proc/uptime').read().split()[0])


@plugin
class UptimeWidget (DashboardWidget):
    name = 'Uptime'

    def init(self):
        self.sensor = Sensor.find('uptime')
        self.append(self.ui.inflate('sensors:value-widget'))

        self.find('icon').text = 'off'
        self.find('name').text = 'Uptime'
        self.find('value').text = str_timedelta(self.sensor.value())
