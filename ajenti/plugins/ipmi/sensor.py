import subprocess

from ajenti.api import *
from ajenti.api.sensors import Sensor
from ajenti.util import cache_value


@plugin
class IPMISensor (Sensor):
    id = 'ipmi'
    timeout = 5

    @cache_value(2)
    def _get_data(self):
        r = {}
        for l in subprocess.check_output(['ipmitool', 'sensor']).splitlines():
            l = l.split('|')
            if len(l) > 2:
                r[l[0].strip()] = (l[1].strip(), l[2].strip())
        return r

    def get_variants(self):
        return sorted(self._get_data().keys())

    def measure(self, variant):
        try:
            return self._get_data()[variant]
        except:
            return (0, '')
