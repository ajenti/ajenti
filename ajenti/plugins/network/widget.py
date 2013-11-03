import psutil
import time

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.util import str_fsize

from api import NetworkManager


@plugin
class TrafficSensor (Sensor):
    id = 'traffic'
    timeout = 5

    def get_variants(self):
        return NetworkManager.get().get_devices()

    def measure(self, device):
        try:
            v = psutil.network_io_counters(pernic=True)[device]
        except KeyError:
            return (0, 0)
        return (v.bytes_sent, v.bytes_recv)


@plugin
class ImmediateTXSensor (Sensor):
    id = 'immediate-tx'
    timeout = 5

    def init(self):
        self.last_tx = {}
        self.last_time = {}

    def get_variants(self):
        return psutil.network_io_counters(pernic=True).keys()

    def measure(self, device):
        try:
            v = psutil.network_io_counters(pernic=True)[device]
        except KeyError:
            return 0
        r = (v.bytes_sent, v.bytes_recv)
        if not self.last_tx.get(device, None):
            self.last_tx[device] = r[0]
            self.last_time[device] = time.time()
            return 0
        else:
            d = (r[0] - self.last_tx[device]) / (1.0 * time.time() - self.last_time[device])
            self.last_tx[device] = r[0]
            self.last_time[device] = time.time()
            return d


@plugin
class ImmediateRXSensor (Sensor):
    id = 'immediate-rx'
    timeout = 5

    def init(self):
        self.last_rx = {}
        self.last_time = {}

    def get_variants(self):
        return psutil.network_io_counters(pernic=True).keys()

    def measure(self, device):
        try:
            v = psutil.network_io_counters(pernic=True)[device]
        except KeyError:
            return 0
        r = (v.bytes_sent, v.bytes_recv)
        if not self.last_rx.get(device, None):
            self.last_rx[device] = r[1]
            self.last_time[device] = time.time()
            return 0
        else:
            d = (r[1] - self.last_rx[device]) / (1.0 * time.time() - self.last_time[device])
            self.last_rx[device] = r[1]
            self.last_time[device] = time.time()
            return d


@plugin
class ImmediateTrafficWidget (ConfigurableWidget):
    name = _('Immediate Traffic')
    icon = 'exchange'

    def on_prepare(self):
        self.sensor = Sensor.find('traffic')
        self.sensor_tx = Sensor.find('immediate-tx')
        self.sensor_rx = Sensor.find('immediate-rx')
        self.append(self.ui.inflate('network:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        self.find('up').text = str_fsize(self.sensor_tx.value(self.config['device'])) + '/s'
        self.find('down').text = str_fsize(self.sensor_rx.value(self.config['device'])) + '/s'

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
class TrafficWidget (ConfigurableWidget):
    name = _('Traffic')
    icon = 'exchange'

    def on_prepare(self):
        self.sensor = Sensor.find('traffic')
        self.append(self.ui.inflate('network:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        u, d = self.sensor.value(self.config['device'])
        self.find('up').text = str_fsize(u)
        self.find('down').text = str_fsize(d)

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
