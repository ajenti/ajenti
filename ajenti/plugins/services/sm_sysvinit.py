import subprocess

from ajenti.api import *

from api import Service, ServiceManager


@plugin
class SysVInitServiceManager (ServiceManager):
    platforms = ['debian']

    def get_all(self):
        r = []
        for line in subprocess.check_output(['service', '--status-all']).splitlines():
            tokens = line.split()
            if len(tokens) < 3:
                continue

            name = tokens[3]
            status = tokens[1]
            if status == '?':
                continue

            s = SysVInitService(name)
            s.running = status == '+'
            r.append(s)
        return r


class SysVInitService (Service):
    source = 'sysvinit'

    def __init__(self, name):
        self.name = name
        self.script = '/etc/init.d/%s' % self.name

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
