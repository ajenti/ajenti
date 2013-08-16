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
        for line in subprocess.check_output(['service', '-l']).splitlines():
            if line:
                s = FreeBSDService(line)
                try:
                    s.refresh()
                    r.append(s)
                except OSError:
                    pass
        return r


class FreeBSDService (Service):
    source = 'rc.d'

    def __init__(self, name):
        self.name = name
        self.script = '/etc/rc.d/%s' % self.name

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
