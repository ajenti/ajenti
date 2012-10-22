from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget

import disks


@plugin
class DiskSpaceWidget (ConfigurableWidget):
    name = 'Disk space'

    def on_prepare(self):
        self.meter = disks.DiskUsageMeter()
        self.append(self.ui.inflate('fstab:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        self.find('usage').text = '%i%%' % self.meter.get_usage(self.config['device'])

    def create_config(self):
        return {'device': ''}

    def on_config_start(self):
        device_list = self.dialog.find('device')
        lst = self.meter.get_devices()
        device_list.items = lst
        device_list.values = lst
        device_list.value = self.config['device']

    def on_config_save(self):
        self.config['device'] = self.dialog.find('device').value
