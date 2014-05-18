from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.util import str_fsize


@plugin
class DiskSpaceWidget (ConfigurableWidget):
    name = _('Disk space')
    icon = 'hdd'

    def on_prepare(self):
        self.sensor = Sensor.find('disk-usage')
        self.append(self.ui.inflate('fstab:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        u, f, t = self.sensor.value(self.config['device'])
        self.find('percent').text = str_fsize(u)
        self.find('usage').value = float(1.0 * u / t)

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


@plugin
class DiskFreeSpaceWidget (DiskSpaceWidget):
    name = _('Free disk space')
    icon = 'hdd'

    def on_prepare(self):
        self.sensor = Sensor.find('disk-usage')
        self.append(self.ui.inflate('fstab:free-widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        u, f, t = self.sensor.value(self.config['device'])
        self.find('value').text = _('%s free') % str_fsize(f)
