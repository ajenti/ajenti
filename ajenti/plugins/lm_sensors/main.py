#coding: utf-8
import subprocess
import re

from ajenti.api import BasePlugin, plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.util import *


class LMSensors (BasePlugin):
    re_temp = re.compile(r'^(?P<name>.+?):\s+\+(?P<value>[\d.]+).+$')

    @cache_value(3)
    def get(self):
        try:
            lines = subprocess.check_output(['sensors']).splitlines()
        except subprocess.CalledProcessError, e:
            return {}  # sensors not configured
        r = {}
        for l in lines:
            m = self.re_temp.match(l)
            if m:
                r[m.groupdict()['name']] = float(m.groupdict()['value'])
        return r


@plugin
class Sensors (Sensor):
    id = 'lm-sensors'
    timeout = 3

    def init(self):
        self.lm = LMSensors()

    def measure(self, variant=None):
        try:
            return self.lm.get()[variant]
        except KeyError:
            return 0

    def get_variants(self):
        return self.lm.get().keys()


@plugin
class TempWidget (ConfigurableWidget):
    name = 'Temperature'
    icon = 'fire'

    def on_prepare(self):
        self.sensor = Sensor.find('lm-sensors')
        self.append(self.ui.inflate('lm_sensors:widget'))

    def on_start(self):
        value = self.sensor.value(self.config['sensor'])
        self.find('name').text = self.config['sensor']
        self.find('value').text = '+%.1f °C' % value

    def create_config(self):
        return {'sensor': ''}

    def on_config_start(self):
        service_list = self.dialog.find('sensor')
        service_list.labels = service_list.values = self.sensor.get_variants()
        service_list.value = self.config['sensor']

    def on_config_save(self):
        self.config['sensor'] = self.dialog.find('sensor').value
