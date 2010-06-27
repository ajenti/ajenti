import os

from ajenti.utils import *

dir_squid = '/etc/squid/'

def is_installed():
    return os.path.exists(dir_squid)
    
def is_running():
    return shell_status('pgrep squid') == 0


class SquidConfig:
    misc = []
    acls = []
    http_access = []
    
    def load(self):
        self.misc = []
        self.acls = []
        self.http_access = []

        ss = open(dir_squid + 'squid.conf').read().split('\n')
        
        for s in ss:
            if len(s) > 0 and s[0] != '#':
                try:
                    s = s.split(' ')
                    k = s[0]
                    v = ' '.join(s[1:])
                    if k == 'acl':
                        v = v.split(' ')
                        an = v[0]
                        av = ' '.join(v[1:])
                        self.acls.append((an, av))
                    elif k == 'http_access':
                        v = v.split(' ')
                        an = v[0]
                        av = ' '.join(v[1:])
                        self.http_access.append((an, av))
                    else:
                        self.misc.append((k, v))
                except:
                    pass
                
    def save(self):
        s = ''
        
        s += '\n# ACLs\n'
        for k,v in self.acls:
            s += 'acl %s %s\n' % (k,v)

        s += '\n# HTTP access\n'
        for k,v in self.http_access:
            s += 'http_access %s %s\n' % (k,v)

        s += '\n# Misc options\n'
        for k,v in self.misc:
            s += '%s %s\n' % (k,v)
            
        with open(dir_squid + 'squid.conf', 'w') as f:
            f.write(s)
