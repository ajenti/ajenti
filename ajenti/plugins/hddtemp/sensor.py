import os
import re
import subprocess

from ajenti.api import *
from ajenti.api.sensors import Sensor


@plugin
class DiskTemperatureSensor (Sensor):
    id = 'hdd-temp'
    timeout = 5

    def get_variants(self):
        r = []
        for s in os.listdir('/dev'):
            if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
                r.append(s)
        return sorted(r)

    def measure(self, device):
        try:
            v = float('0' + subprocess.check_output(
                ['hddtemp', '/dev/%s' % device, '-uC', '-qn'], stderr=None).strip())
            return v
        except:
            return 0
