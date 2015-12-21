import dbus
import os

import subprocess
import logging

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager


class SystemdService (Service):
    source = 'systemd'

    def __init__(self, name):
        self.name = name
        self.running = False

    def refresh(self):
        self.running = subprocess.call(['systemctl', 'is-active', self.name]) == 0

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('restart')

    def command(self, cmd):
        return subprocess.call(['systemctl', cmd, self.name], close_fds=True)


@plugin
class SystemdServiceManager (ServiceManager):
    def init(self):
        self.bus = dbus.SystemBus()
        self.systemd = self.bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        self.interface = dbus.Interface(self.systemd, 'org.freedesktop.systemd1.Manager')

    @classmethod
    def verify(cls):
        if subprocess.call(['which', 'systemctl']) != 0:
            return False
        try:
            c = cls()
            c.init()
            c.get_all()
            return True
        except Exception, e:
            logging.info('Disabling systemd service manager: %s' % str(e))
            return False

    @cache_value(1)
    def get_all(self):
        unit_files = self.interface.ListUnitFiles() 
        r = []
        for unit_file in unit_files:
            if str(unit_file[0]).endswith('.service'):
                name = str(unit_file[0])
                name = os.path.splitext(name)[0]
                name = os.path.split(name)[1]
                r.append(SystemdService(name))

        units = self.interface.ListUnits()
        for unit in units:
            name = str(unit[0])
            name = os.path.splitext(name)[0]
            for service in r:
                if service.name == name:
                    service.running = str(unit[4]) == 'running'

        return r
