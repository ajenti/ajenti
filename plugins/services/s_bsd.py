import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class BSDServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['freebsd']

    def list_all(self):
        r = []
        for s in os.listdir('/etc/rc.d'):
            svc = apis.services.Service()
            svc.name = s
            svc.status = 'running' \
                    if os.path.exists('/var/run/%s.pid'%s)\
                    else 'stopped'
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        s = shell('/etc/rc.d/' + name + ' status')
        return 'running' if 'running' in s else 'stopped'

    def start(self, name):
        shell('/etc/rc.d/' + name + ' start')

    def stop(self, name):
        shell('/etc/rc.d/' + name + ' stop')

    def restart(self, name):
        shell('/etc/rc.d/' + name + ' restart')
