import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class ArchServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['Arch']

    def list_all(self):
        r = []
        running = os.listdir('/var/run/daemons')
        for s in os.listdir('/etc/rc.d'):
            svc = apis.services.Service()
            svc.name = s
            svc.status = 'running' if s in running else 'stopped'
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def start(self, name):
        shell('/etc/rc.d/' + name + ' start')

    def stop(self, name):
        shell('/etc/rc.d/' + name + ' stop')

    def restart(self, name):
        shell('/etc/rc.d/' + name + ' restart')
