from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_fsize


@plugin
class MemorySensor (Sensor):
    id = 'memory'
    timeout = 5

    def measure(self, variant):
        memdata = dict([
            (l.split()[0].strip(':'),
             int(l.split()[1]) * 1024)
            for l in open('/proc/meminfo').read().split('\n')
            if len(l) > 0
        ])
        total = memdata['MemTotal']
        free = memdata['MemFree'] + memdata['Buffers'] + memdata['Cached']
        return (total - free, total)


@plugin
class MemoryWidget (DashboardWidget):
    name = 'Memory usage'

    def init(self):
        self.sensor = Sensor.find('memory')
        self.append(self.ui.inflate('sensors:progressbar-widget'))
        self.find('icon').icon = 'tasks'
        self.find('name').text = 'Memory usage'
        value = self.sensor.value()
        self.find('value').text = str_fsize(value[0])
        self.find('progress').value = 1.0 * value[0] / value[1]
