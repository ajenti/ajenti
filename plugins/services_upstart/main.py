from ajenti.com import *
from ajenti.utils import *

from plugins.services.api import *

class UpstartServiceManager(Plugin):
    implements(IServiceManager)
    platform = ['Debian', 'Ubuntu']
    
    def list_all(self):
        r = []
        for s in shell('service --status-all').split('\n'):
            ss = s.split()
            if ss[1] != '?':
                svc = Service()
                svc.name = ss[3]
                svc.status = 'running' if ss[1] == '+' else 'stopped'            
                r.append(svc)
                
        return sorted(r, key=lambda s: s.name)
        
    def start(self, name):
        shell('service ' + name + ' start')
        
    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
 
