#coding: utf-8
from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class IPMIWidget (ConfigurableWidget):
    name = _('IPMI Sensor')
    icon = 'dashboard'

    def on_prepare(self):
        self.sensor = Sensor.find('ipmi')
        self.append(self.ui.inflate('ipmi:widget'))

    def on_start(self):
        self.find('variant').text = self.config['variant']
        v = self.sensor.value(self.config['variant'])
        self.find('value').text = v[0]
        self.find('unit').text = v[1]

    def create_config(self):
        return {'variant': ''}

    def on_config_start(self):
        v_list = self.dialog.find('variant')
        lst = self.sensor.get_variants()
        v_list.labels = lst
        v_list.values = lst
        v_list.value = self.config['variant']

    def on_config_save(self):
        self.config['variant'] = self.dialog.find('variant').value
