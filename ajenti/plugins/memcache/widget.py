import os
import socket

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_fsize


@plugin
class MemcacheSensor (Sensor):
    id = 'memcache'
    timeout = 5

    def measure(self, variant=None):
        sock_path = '/var/run/memcached.sock'
        if os.path.exists(sock_path):
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_path)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 11211))
        s.send('stats\r\n')
        data = s.recv(10240)
        s.close()
        d = dict([
            l.split()[1:]
            for l in data.splitlines() if len(l.split()) == 3
        ])
        return (int(d['bytes']), int(d['limit_maxbytes']))


@plugin
class MemcachedWidget (DashboardWidget):
    name = _('Memcache memory usage')
    icon = 'tasks'

    def init(self):
        self.sensor = Sensor.find('memcache')
        self.append(self.ui.inflate('memcache:widget'))
        value = self.sensor.value()
        self.find('value').text = str_fsize(value[0])
        self.find('progress').value = 1.0 * value[0] / value[1]
