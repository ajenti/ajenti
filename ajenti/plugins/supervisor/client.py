import subprocess

from ajenti.api import *


@plugin
class Client (object):
    def test(self):
        return subprocess.call(['supervisorctl', 'status']) == 0

    def run(self, *cmds):
        return subprocess.check_output(['supervisorctl'] + list(cmds))

    def fill(self, programs):
        for p in programs:
            p.status = ''
            p.icon = ''
        for l in self.run('status').splitlines():
            l = l.split(None, 2)
            for p in programs:
                if p.name == l[0]:
                    p.running = len(l) > 2 and l[1] == 'RUNNING'
                    p.status = l[2] if len(l) > 2 else ''
                    p.icon = 'play'

    def start(self, id):
        self.run('start', id)

    def restart(self, id):
        self.run('restart', id)

    def stop(self, id):
        self.run('stop', id)

    def tail(self, id):
        return self.run('tail', id)
