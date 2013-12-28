try:
    import dbus
except ImportError:
    pass

import subprocess
import logging

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager


@plugin
class SystemdServiceManager (ServiceManager):
    platforms = ['arch']

    def init(self):
        self.bus = dbus.SystemBus()
        self.systemd = self.bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        self.interface = dbus.Interface(self.systemd, 'org.freedesktop.systemd1.Manager')

    @classmethod
    def verify(cls):
        try:
            c = cls()
            c.init()
            return True
        except:
            return False

    @cache_value(1)
    def get_all(self):
        try:
            units = self.interface.ListUnits()
            r = []
            logging.debug('units size: %i' % len(units))
            for unit in units:
                if (unit[0].endswith('.service')):
#                    logging.debug('================== service ==================')
#                    logging.debug('unit: %s' % unit[0])
#                    logging.debug('desc: %s' % unit[1])
#                    logging.debug('status: %s' % unit[2])
#                    logging.debug('isactive: %s' % unit[3])
#                    logging.debug('plugged: %s' % unit[4])
#                    logging.debug('path: %s' % unit[6])

                    s = SystemdService(str(unit[0]))
                    s.running = (str(unit[4]) == 'running')
                    r.append(s)

            return r
        except dbus.DBusException:
            return []


class SystemdService (Service):
    source = 'systemd'

    def __init__(self, name):
        self.name = name

    def refresh(self):
        self.running = 'running' in subprocess.check_output(['systemctl', 'status', self.name])

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('restart')

    def command(self, cmd):
        subprocess.Popen(['systemctl', cmd,  self.name], close_fds=True).wait()
