import os
import subprocess

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager


@plugin
class FreeBSDServiceManager (ServiceManager):
    platforms = ['freebsd']

    @cache_value(1)
    def get_all(self):
        r = []
        dirs = ['/etc/rc.d', '/usr/local/etc/rc.d']
        for line in subprocess.check_output(['service', '-l']).splitlines():
            if line:
                for d in dirs:
                    if os.path.exists(os.path.join(d, line)):
                        s = FreeBSDService(line, d)
                        try:
                            s.refresh()
                            r.append(s)
                        except OSError:
                            pass
        return r


class FreeBSDService (Service):
    source = 'rc.d'

    def __init__(self, name, dir):
        self.name = name
        self.script = os.path.join(dir, self.name)

    def refresh(self):
        self.running = subprocess.call([self.script, 'status']) == 0

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('restart')

    def command(self, cmd):
        subprocess.call([self.script, cmd])
