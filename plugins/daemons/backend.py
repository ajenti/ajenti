from ajenti.com import *
from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import UI
from ajenti import apis


class Daemons(Plugin):
    def __init__(self):
        self.file = '/etc/daemon.conf'
        
    def list_all(self):
        r = []
        for l in open(self.file, 'r'):
            l = l.strip()
            if not l.startswith('#'):
                if ' ' in l:
                    r.append(Daemon(*(l.strip().split(' ', 1))))
        return sorted(r, key=lambda x: x.name)

    def save(self, items):
        f = open(self.file, 'w')
        for i in items:
            f.write('%s '%i.name)
            x = []
            for k in i.opts.keys():
                if i.opts[k] == None:
                    x.append(k)
                else:
                    x.append('%s="%s"'%(k,i.opts[k].strip(' "')))
            f.write(','.join(x))
            f.write('\n')
        f.close()
    
    def start(self, name):
        return shell('daemon --name "%s"'%name)

    def restart(self, name):
        return shell('daemon --restart "%s"'%name)
        
    def stop(self, name):
        return shell('daemon --stop "%s"'%name)

        
class Daemon:
    def __init__(self, name, s):
        self.name = name
        self.opts = {}
        for x in s.split(','):
            v = None
            if '=' in x:
                k,v = x.split('=')
                v = v.strip(' "')
            else:
                k = x
            self.opts[k.strip()] = v
        print self.name, self.opts
         
    @property
    def running(self):
        return shell_status('daemon --running --name "%s"'%self.name) == 0
        
        
options = [
    'command',
    'user',
    'chroot',
    'chdir',
    'umask',
    'attempts',
    'delay',
    'limit',
    'output',
    'stdout',
    'stderr',
]        
