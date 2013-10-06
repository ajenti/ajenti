import subprocess

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget


@plugin
class UPSChargeSensor (Sensor):
    id = 'ups'
    timeout = 2

    def measure(self, variant=None):
        data = {}
        for l in subprocess.check_output('apcaccess').splitlines():
            if l and ':' in l:
                k,v = l.split(':', 1)
                k = k.strip()
                v = v.strip()
                data[k] = v

        return (float(data.get('BCHARGE', '0 Percent').split()[0]) / 100.0, data.get('TIMELEFT', 'Unknown'))


@plugin
class UPSWidget (DashboardWidget):
    name = 'UPS'
    icon = 'bolt'

    def init(self):
        self.sensor = Sensor.find('ups')
        self.append(self.ui.inflate('apcups:widget'))
        value = self.sensor.value()
        self.find('charge').value = value[0]
        self.find('time').text = value[1]
