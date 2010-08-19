import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class UpstartServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['Debian', 'Ubuntu']

    def list_all(self):
        r = []
        for s in os.listdir('/etc/init'):
            if len(s) > 5:
                s = s[:-5]
                svc = apis.services.Service()
                svc.name = s
                r.append(svc)
                if 'start/running' in shell('service %s status' % s):
                    svc.status = 'running'
                else:
                    svc.status = 'stopped'

        return sorted(r, key=lambda s: s.name)

    def start(self, name):
        shell('service ' + name + ' start')

    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
