import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis
from ajenti.api import *

    
class GentooServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['gentoo']

    def list_all(self):
        r = []
                
        for s in shell('rc-update show -v').split('\n'):
            try:
                print '>', s.split()[0], 'started' in shell('/etc/init.d/%s status'%s.split()[0])
                s = s.split()[0]
                svc = apis.services.Service()
                svc.name = s
                svc.mgr = self
                r.append(svc)
            except:
                pass
            
        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        s = shell('/etc/init.d/%s status'%name)
        return 'started' in s

    def start(self, name):
        shell('/etc/init.d/%s start'%name)

    def stop(self, name):
        shell('/etc/init.d/%s stop'%name)

    def restart(self, name):
        shell('/etc/init.d/%s restart'%name)
