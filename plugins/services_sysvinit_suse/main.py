import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class SuseInitServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['openSUSE']

    def list_all(self):
        r = []
        for s in shell('chkconfig').split('\n'):
            s = ' '.join(s.split()[:-1])
            svc = apis.services.Service()
            svc.name = s
            svc.status = 'running' if 'running' in shell('/etc/init.d/%s status'%s) else 'stopped'
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def start(self, name):
        shell('service ' + name + ' start')

    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
