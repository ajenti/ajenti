from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

class UpstartServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['Debian', 'Ubuntu']
    
    def list_all(self):
        r = []
        for s in shell('service --status-all').split('\n'):
            if s != '':
                ss = s.split()
                if ss[1] != '?':
                    svc = apis.services.Service()
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
 
