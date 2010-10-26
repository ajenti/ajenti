import re
import os

from ajenti.utils import *
from ajenti.plugins.uzuri_common import ClusteredConfig
from ajenti.com import *
from ajenti import apis


class Host:
    def __init__(self):
        self.ip = '';
        self.name = '';
        self.aliases = '';


class Config(ClusteredConfig):
    name = 'Hosts'
    id = 'hosts'
    files = [('/etc', 'hosts'), ('/etc', 'hostname'), ('/etc', 'rc.conf')] 
    
    @property
    def run_after(self):
        return ['hostname ' + self.gethostname()]
    
    def read(self):
        ss = self.open('/etc/hosts', 'r').read().split('\n')
        r = []

        for s in ss:
            if s != '' and s[0] != '#':
                try:
                    s = s.split()
                    h = Host()
                    try:
                        h.ip = s[0]
                        h.name = s[1]
                        for i in range(2, len(s)):
                            h.aliases += '%s ' % s[i]
                        h.aliases = h.aliases.rstrip();
                    except:
                        pass
                    r.append(h)
                except:
                    pass

        return r

    def save(self, hh):
        d = ''
        for h in hh:
            d += '%s\t%s\t%s\n' % (h.ip, h.name, h.aliases)
        with self.open('/etc/hosts', 'w') as f:
            f.write(d)
            
    def gethostname(self):
        return self.app.get_backend(IHostnameManager).gethostname(self)
        
    def sethostname(self, hn):
        self.app.get_backend(IHostnameManager).sethostname(self, hn)
            


class IHostnameManager(Interface):
    def gethostname(self, cc):
        pass
        
    def sethostname(self, cc, hn):
        pass
        
        
class LinuxGenericHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['debian', 'opensuse']
    
    def gethostname(self, cc):
        return cc.open('/etc/hostname').read()
        
    def sethostname(self, cc, hn):
        cc.open('/etc/hostname', 'w').write(hn)


class ArchHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['arch']
    
    def gethostname(self, cc):
        return apis.rcconf.RCConf(self.app).get_param('HOSTNAME')
        
    def sethostname(self, cc, hn):
        apis.rcconf.RCConf(self.app).set_param('HOSTNAME', hn, near='HOSTNAME')
        
        
class BSDHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['freebsd']
    
    def gethostname(self, cc):
        return apis.rcconf.RCConf(self.app).get_param('hostname')
        
    def sethostname(self, cc, hn):
        apis.rcconf.RCConf(self.app).set_param('hostname', hn, near='hostname')
