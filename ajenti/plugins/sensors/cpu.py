import gevent

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.ui.binder import Binder


@plugin
class CPUSensor (Sensor):
    id = 'cpu'
    timeout = 3

    def init(self):
        self._value = [0] * len(self.get_jiffies())
        gevent.spawn(self.worker)

    def measure(self, variant=None):
        return self._value

    def worker(self):
        old = new = self.get_jiffies()
        while True:
            r = []
            for o, n in zip(old, new):
                t1, i1, w1 = o
                t2, i2, w2 = n
                dt = t2 - t1
                di = i2 - i1
                #dw = w2 - self.w1
                if dt > 0:
                    idle = 1.0 * di / dt
                else:
                    idle = 1.0
                #wait = 1.0 * dw / dt # iowait
                r.append(1.0 - idle)
            self._value = r

            old = new
            gevent.sleep(self.timeout)
            new = self.get_jiffies()

    def get_jiffies(self):
        r = []
        for l in open('/proc/stat', 'r').read().split('\n'):
            l = l.split()
            if len(l) > 5 and l[0] != 'cpu' and l[0].startswith('cpu'):
                idle = int(l[4])
                iowait = int(l[5])
                total = sum(int(x) for x in l[1:9])
                r.append((total, idle, iowait))
        return r


@plugin
class CPUWidget (DashboardWidget):
    name = 'CPU usage'
    icon = 'signal'

    def init(self):
        self.sensor = Sensor.find('cpu')
        self.append(self.ui.inflate('sensors:cpu-widget'))
        self.find('icon').icon = 'signal'
        self.find('name').text = 'CPU usage'
        for value in self.sensor.value():
            l = self.ui.inflate('sensors:cpu-line')
            l.find('progress').value = value
            l.find('value').text = '%i%%' % int(value * 100)
            self.find('lines').append(l)
