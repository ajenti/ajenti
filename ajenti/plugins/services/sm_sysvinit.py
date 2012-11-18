import subprocess

from ajenti.api import *

from api import Service, ServiceManager


@plugin
class SysVInitServiceManager (ServiceManager):
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
    def __init__(self, name):
        self.name = name
        self.script = '/etc/init.d/%s' % self.name

    def start(self):
        subprocess.call([self.script, 'start'])

    def stop(self):
        subprocess.call([self.script, 'stop'])

    def restart(self):
        subprocess.call([self.script, 'restart'])
