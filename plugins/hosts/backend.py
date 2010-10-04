import re
import os

from ajenti.utils import *
from ajenti.plugins.uzuri_common import ClusteredConfig

class Host:
    def __init__(self):
        self.ip = '';
        self.name = '';
        self.aliases = '';


class Config(ClusteredConfig):
    name = 'Hosts'
    id = 'hosts'
    files = [('/etc', 'hosts'), ('/etc', 'hostname')] 
    
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
        return self.open('/etc/hostname').read()
        
    def sethostname(self, hn):
        return self.open('/etc/hostname', 'w').write(hn)
