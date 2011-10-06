from ConfigParser import ConfigParser

from ajenti.com import Plugin
from ajenti.utils import shell, shell_status


class SVClient (Plugin):
    icon = '/dl/supervisor/icon.png'

    def test(self):
        return shell_status('supervisorctl status') == 0

    def run(self, cmd):
        return shell('supervisorctl ' + cmd)

    def status(self):
        r = []
        for l in self.run('status').splitlines():
            l = l.split(None, 2)
            r.append({
                'name': l[0],
                'status': '' if len(l)<2 else l[1],
                'info': '' if len(l)<3 else l[2],
            })
        return r

    def start(self, id):
        self.run('start ' + id)

    def restart(self, id):
        self.run('restart ' + id)

    def stop(self, id):
        self.run('stop ' + id)

    def tail(self, id):
        return self.run('tail ' + id)
