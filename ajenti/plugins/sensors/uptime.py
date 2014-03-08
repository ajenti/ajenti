import psutil
import time

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_timedelta


@plugin
class UnixUptimeSensor (Sensor):
    id = 'uptime'
    timeout = 1

    def measure(self, variant):
        return time.time() - psutil.BOOT_TIME


@plugin
class UptimeWidget (DashboardWidget):
    name = _('Uptime')
    icon = 'off'

    def init(self):
        self.sensor = Sensor.find('uptime')
        self.append(self.ui.inflate('sensors:value-widget'))

        self.find('icon').text = 'off'
        self.find('name').text = 'Uptime'
        self.find('value').text = str_timedelta(self.sensor.value())
