import gevent

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget


@plugin
class CPUSensor (Sensor):
    id = 'cpu'
    timeout = 1

    def init(self):
        self._value = 0
        gevent.spawn(self.worker)

    def measure(self, variant=None):
        return self._value

    def worker(self):
        while True:
            self.t1, self.i1, self.w1 = self.get_jiffies()
            gevent.sleep(1)
            t2, i2, w2 = self.get_jiffies()
            dt = t2 - self.t1
            di = i2 - self.i1
            #dw = w2 - self.w1
            self.t1, self.i1, self.w1 = t2, i2, w2
            idle = 1.0 * di / dt
            #wait = 1.0 * dw / dt # iowait
            self._value = 1.0 - idle

    def get_jiffies(self):
        l = filter(None, open('/proc/stat', 'r').read().split('\n')[0].split())
        idle = int(l[4])
        iowait = int(l[5])
        total = sum(int(x) for x in l[1:9])
        return total, idle, iowait


@plugin
class CPUWidget (DashboardWidget):
    name = 'CPU usage'

    def init(self):
        self.sensor = Sensor.find('cpu')
        self.append(self.ui.inflate('sensors:progressbar-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = 'CPU usage'
        value = self.sensor.value()
        self.find('value').text = '%i%%' % (value * 100)
        self.find('progress').value = value
