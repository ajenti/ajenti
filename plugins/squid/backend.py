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
        for k,v in self.misc:
            print '%s = %s' % (k,v)
