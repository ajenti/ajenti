from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class LoadSensor (Sensor):
    id = 'load'
    timeout = 1

    def measure(self, variant):
        idx = self.get_variants().index(variant)
        return float(open('/proc/loadavg').read().split()[idx])

    def get_variants(self):
        return ['1 min', '5 min', '15 min']


@plugin
class LoadWidget (ConfigurableWidget):
    name = 'Load average'
    icon = 'signal'

    def on_prepare(self):
        self.sensor = Sensor.find('load')
        self.append(self.ui.inflate('sensors:value-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = 'Load average'
        self.find('value').text = '&nbsp;&nbsp;'.join(str(self.sensor.value(x)) for x in self.sensor.get_variants())
