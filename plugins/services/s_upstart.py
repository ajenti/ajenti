import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis
from ajenti.api import *


class UpstartServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['debian']

    def list_all(self):
        r = []
        found = []

        for s in shell('service --status-all').split('\n'):
            if len(s) > 3 and s[3] != '?':
                name = s.split()[3]
                if not name in found:
                    found.append(name)
                    svc = apis.services.Service()
                    svc.name = name
                    svc.status = 'running' if s[3] == '+' else 'stopped'
                    r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        l = [x.status for x in self.list_all() if x.name == name]
        if len(l) == 0:
            return 'stopped'
        return l[0]

    def start(self, name):
        shell('service ' + name + ' start')

    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
