from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class DiskSpaceWidget (ConfigurableWidget):
    name = 'Disk space'

    def on_prepare(self):
        self.sensor = Sensor.find('disk-usage')
        self.append(self.ui.inflate('fstab:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        value = self.sensor.value(self.config['device'])
        self.find('percent').text = '%i%%' % value
        self.find('usage').value = float(value) / 100

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
