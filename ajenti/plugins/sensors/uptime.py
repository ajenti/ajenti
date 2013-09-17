import ctypes
import struct
import time

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_timedelta


@plugin
class LinuxUptimeSensor (Sensor):
    id = 'uptime'
    platforms = ['debian', 'centos']
    timeout = 1

    def measure(self, variant):
        return float(open('/proc/uptime').read().split()[0])


@plugin
class BSDUptimeSensor (Sensor):
    id = 'uptime'
    platforms = ['freebsd']
    timeout = 1

    def measure(self):
        """
        by Koen Crolla
        https://github.com/Cairnarvon/uptime/blob/master/src/__init__.py
        """

        try:
            libc = ctypes.CDLL('libc.so')
        except AttributeError:
            return None
        except OSError:
            # OS X; can't use ctypes.util.find_library because that creates
            # a new process on Linux, which is undesirable.
            try:
                libc = ctypes.CDLL('libc.dylib')
            except OSError:
                return None

        if not hasattr(libc, 'sysctlbyname'):
            # Not BSD.
            return None

        # Determine how much space we need for the response.
        sz = ctypes.c_uint(0)
        libc.sysctlbyname('kern.boottime', None, ctypes.byref(sz), None, 0)
        if sz.value != struct.calcsize('@LL'):
            # Unexpected, let's give up.
            return None

        # For real now.
        buf = ctypes.create_string_buffer(sz.value)
        libc.sysctlbyname('kern.boottime', buf, ctypes.byref(sz), None, 0)
        sec, usec = struct.unpack('@LL', buf.raw)

        # OS X disagrees what that second value is.
        if usec > 1000000:
            usec = 0.

        __boottime = sec + usec / 1000000.
        up = time.time() - __boottime
        if up < 0:
            up = None
        return up


@plugin
class UptimeWidget (DashboardWidget):
    name = _('Uptime')
    icon = 'off'

    def init(self):
        self.sensor = Sensor.find('uptime')
        self.append(self.ui.inflate('sensors:value-widget'))

        self.find('icon').text = 'off'
        self.find('name').text = 'Uptime'
        self.find('value').text = str_timedelta(self.sensor.value())
