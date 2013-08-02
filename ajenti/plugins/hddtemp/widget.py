#coding: utf-8
from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class HDDTempWidget (ConfigurableWidget):
    name = _('HDD Temperature')
    icon = 'hdd'

    def on_prepare(self):
        self.sensor = Sensor.find('hdd-temp')
        self.append(self.ui.inflate('hddtemp:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        v = self.sensor.value(self.config['device'])
        self.find('value').text = '%.2f °C' % v

    def create_config(self):
        return {'device': ''}

    def on_config_start(self):
        device_list = self.dialog.find('device')
        lst = self.sensor.get_variants()
        device_list.labels = lst
        device_list.values = lst
        device_list.value = self.config['device']

    def on_config_save(self):
        self.config['device'] = self.dialog.find('device').value
