import psutil

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_fsize


@plugin
class MemorySensor (Sensor):
    id = 'memory'
    timeout = 5

    def measure(self, variant):
        v = psutil.virtual_memory()
        return (v.total - v.available, v.total)


@plugin
class SwapSensor (Sensor):
    id = 'swap'
    timeout = 5

    def measure(self, variant):
        v = psutil.swap_memory()
        return (v.used, v.total)


@plugin
class MemoryWidget (DashboardWidget):
    name = _('Memory usage')
    icon = 'tasks'

    def init(self):
        self.sensor = Sensor.find('memory')
        self.append(self.ui.inflate('sensors:progressbar-widget'))
        self.find('icon').icon = 'tasks'
        self.find('name').text = _('Memory usage')
        value = self.sensor.value()
        self.find('value').text = str_fsize(value[0])
        self.find('progress').value = 1.0 * value[0] / value[1]


@plugin
class SwapWidget (DashboardWidget):
    name = _('Swap usage')
    icon = 'hdd'

    def init(self):
        self.sensor = Sensor.find('swap')
        self.append(self.ui.inflate('sensors:progressbar-widget'))
        self.find('icon').icon = 'hdd'
        self.find('name').text = _('Swap usage')
        value = self.sensor.value()
        self.find('value').text = str_fsize(value[0])
        if value[1] > 0:
            frac = 1.0 * value[0] / value[1]
        else:
            frac = 0
        self.find('progress').value = frac
