import os
import psutil

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.util import str_fsize


@plugin
class ImmediateWriteSensor (Sensor):
    id = 'immediate-write'
    timeout = 5

    @classmethod
    def verify(cls):
        return os.path.exists('/proc/diskstats')

    def init(self):
        self.last_write = {}

    def get_variants(self):
        return psutil.disk_io_counters(perdisk=True).keys()

    def measure(self, device):
        try:
            v = psutil.disk_io_counters(perdisk=True)[device]
        except KeyError:
            return 0
        if not self.last_write.get(device, None):
            self.last_write[device] = v.write_bytes
            return 0
        else:
            d = v.write_bytes - self.last_write[device]
            self.last_write[device] = v.write_bytes
            return d


@plugin
class ImmediateReadSensor (Sensor):
    id = 'immediate-read'
    timeout = 5

    @classmethod
    def verify(cls):
        return os.path.exists('/proc/diskstats')

    def init(self):
        self.last_read = {}

    def get_variants(self):
        return psutil.disk_io_counters(perdisk=True).keys()

    def measure(self, device):
        try:
            v = psutil.disk_io_counters(perdisk=True)[device]
        except KeyError:
            return 0
        if not self.last_read.get(device, None):
            self.last_read[device] = v.read_bytes
            return 0
        else:
            d = v.read_bytes - self.last_read[device]
            self.last_read[device] = v.read_bytes
            return d


@plugin
class ImmediateIOWidget (ConfigurableWidget):
    name = _('Immediate I/O')
    icon = 'hdd'

    @classmethod
    def verify(cls):
        return os.path.exists('/proc/diskstats')

    def on_prepare(self):
        self.sensor_write = Sensor.find('immediate-write')
        self.sensor_read = Sensor.find('immediate-read')
        self.append(self.ui.inflate('fstab:iio-widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        self.find('up').text = str_fsize(self.sensor_write.value(self.config['device'])) + '/s'
        self.find('down').text = str_fsize(self.sensor_read.value(self.config['device'])) + '/s'

    def create_config(self):
        return {'device': ''}

    def on_config_start(self):
        device_list = self.dialog.find('device')
        lst = self.sensor_write.get_variants()
        device_list.labels = lst
        device_list.values = lst
        device_list.value = self.config['device']

    def on_config_save(self):
        self.config['device'] = self.dialog.find('device').value
