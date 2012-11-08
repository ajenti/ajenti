import platform

from ajenti.api import *
from ajenti.api.sensors import Sensor


@plugin
class HostnameSensor (Sensor):
    id = 'hostname'
    timeout = 60

    def measure(self, variant=None):
        return platform.node()
