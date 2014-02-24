import subprocess
import re
import os

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class HDPARMSensor (Sensor):
    id = 'hdparm_state'
    timeout = 5

    def get_variants(self):
        r = []
        for s in os.listdir('/dev'):
            if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
                r.append(s)
        return sorted(r)

    def measure(self, path):
        """
        returns state string
        """
        if not path:
            return -1
        output = re.split("\n", subprocess.check_output(['hdparm', '-C', '/dev/' + path]))
        r = re.match("(\s).*:(\s)+(.*)$", output[2])
        if r is None:
            return 0
        return r.group(3)


@plugin
class HDPARMWidget (ConfigurableWidget):
    name = _('HDD drive state')
    icon = 'hdd'

    def on_prepare(self):
        self.sensor = Sensor.find('hdparm_state')
        self.append(self.ui.inflate('smartctl:widget'))

    def on_start(self):
        self.find('device').text = self.config['device']
        v = self.sensor.value(self.config['device'])

        if v == 0:
            v = _('No data')

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
