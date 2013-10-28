import subprocess
import re
import os

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class SMARTSensor (Sensor):
    id = 'smart'
    timeout = 5

    def get_variants(self):
        r = []
        for s in os.listdir('/dev'):
            if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
                r.append(s)
        return sorted(r)

    def measure(self, path):
        """
        -1 = No SMART
        0  = DISK FAILING
        1  = PRE-FAIL
        2  = Unknown error
        3  = Errors in log
        4  = DISK OK
        """
        if not path:
            return -1
        r = subprocess.call(['smartctl', '-H', '/dev/' + path])
        if r & 2:
            return -1
        if r & 8:
            return 0
        if r & 16:
            return 1
        if r & 64:
            return 3
        if r == 0:
            return 4
        return 2


@plugin
class SMARTWidget (ConfigurableWidget):
    name = 'S.M.A.R.T.'
    icon = 'hdd'

    def on_prepare(self):
        self.sensor = Sensor.find('smart')
        self.append(self.ui.inflate('smartctl:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        v = self.sensor.value(self.config['device'])
        v = {
            -1: _('No data'),
            0: _('FAILING'),
            1: _('PRE-FAIL'),
            2: _('Unknown error'),
            3: _('Errors in log'),
            4: 'OK'
        }[v]
        self.find('value').text = v

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
