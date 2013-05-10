import psutil

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.util import str_fsize


@plugin
class TrafficSensor (Sensor):
    id = 'traffic'
    timeout = 5

    def get_variants(self):
        return psutil.network_io_counters(pernic=True).keys()

    def measure(self, device):
        try:
            v = psutil.network_io_counters(pernic=True)[device]
        except KeyError:
            return (0, 0)
        return (v.bytes_sent, v.bytes_recv)


@plugin
class ImmediateTrafficSensor (Sensor):
    id = 'immediate-traffic'
    timeout = 5

    def init(self):
        self.last_tx = {}
        self.last_rx = {}

    def get_variants(self):
        return psutil.network_io_counters(pernic=True).keys()

    def measure(self, device):
        try:
            v = psutil.network_io_counters(pernic=True)[device]
        except KeyError:
            return (0, 0)
        r = (v.bytes_sent, v.bytes_recv)
        if not self.last_tx.get(device, None):
            self.last_tx[device], self.last_rx[device] = r
            return (0, 0)
        else:
            d = (r[0] - self.last_tx[device], r[1] - self.last_rx[device])
            self.last_tx[device], self.last_rx[device] = r
            return d

@plugin
class TrafficWidget (ConfigurableWidget):
    name = 'Traffic'
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
