import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class ArchServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['arch']

    def list_all(self):
        r = []
        for s in os.listdir('/etc/rc.d'):
            svc = apis.services.Service()
            svc.name = s
            svc.mgr = self
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        running = os.listdir('/var/run/daemons')
        return 'running' if name in running else 'stopped'

    def start(self, name):
        shell('/etc/rc.d/' + name + ' start')

    def stop(self, name):
        shell('/etc/rc.d/' + name + ' stop')

    def restart(self, name):
        shell('/etc/rc.d/' + name + ' restart')
