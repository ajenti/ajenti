import subprocess

from ajenti.api import *
from ajenti.plugins.services.api import Service, ServiceManager


@plugin
class SupervisorServiceManager (ServiceManager):
    def test(self):
        return subprocess.call(['supervisorctl', 'status']) == 0

    def run(self, *cmds):
        return subprocess.check_output(['supervisorctl'] + list(cmds))

    def get_all(self):
        r = []
        try:
            lines = self.run('status').splitlines()
        except:
            return []

        for l in lines:
            if l:
                l = l.split(None, 2)
                s = SupervisorService()
                s.name = l[0]
                s.running = len(l) > 2 and l[1] == 'RUNNING'
                s.status = l[2] if len(l) > 2 else ''
                r.append(s)
        return r

    def fill(self, programs):
        for p in programs:
            p.status = ''
            p.icon = ''
        for s in self.get_all():
            for p in programs:
                if p.name == s.name:
                    p.running = s.running
                    p.status = s.status
                    p.icon = 'play' if p.running else None


class SupervisorService (Service):
    source = 'supervisord'

    def __init__(self):
        self.name = None
        self.running = False

    def run(self, *cmds):
        return subprocess.check_output(['supervisorctl'] + list(cmds))

    @property
    def icon(self):
        return 'play' if self.running else None

    def start(self):
        self.run('start', self.name)

    def stop(self):
        self.run('stop', self.name)

    def restart(self):
        self.run('restart', self.name)

    def tail(self, id):
        return self.run('tail', self.name)
