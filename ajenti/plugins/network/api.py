import psutil

from ajenti.api import *


@plugin
class NetworkManager (BasePlugin):
    def get_devices(self):
        return psutil.network_io_counters(pernic=True).keys()
