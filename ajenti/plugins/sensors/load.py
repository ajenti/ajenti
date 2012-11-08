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

    def on_prepare(self):
        self.sensor = Sensor.find('load')
        self.append(self.ui.inflate('sensors:value-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = 'Load average'
        self.find('value').text = '&nbsp;&nbsp;'.join(str(self.sensor.value(x)) for x in self.sensor.get_variants())

"""
@plugin
class LoadWidget (ConfigurableWidget):
    name = 'Load average'

    def on_prepare(self):
        self.sensor = Sensor.find('load')
        self.append(self.ui.inflate('sensors:value-widget'))

    def on_start(self):
        self.find('icon').icon = 'signal'
        value = self.sensor.value(self.config['variant'])
        self.find('name').text = '%s min' % self.config['variant']
        self.find('value').text = str(value)

    def create_config(self):
        return {'variant': ''}

    def on_config_start(self):
        variant_list = self.dialog.find('variant')
        lst = self.sensor.get_variants()
        variant_list.items = lst
        variant_list.values = lst
        variant_list.value = self.config['variant']

    def on_config_save(self):
        self.config['variant'] = self.dialog.find('variant').value
"""