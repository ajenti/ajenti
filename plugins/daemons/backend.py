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
            if not l.strip().startswith('#'):
                if ' ' in l and l != ' ':
                    r.append(Daemon(*(l.strip().split(' ', 1))))
        return sorted(r, key=lambda x: x.name)

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
                v = v.strip()
            else:
                k = x
            self.opts[k.strip()] = v
        print self.name, self.opts
         
    @property
    def running(self):
        return shell_status('daemon --running --name "%s"'%self.name) == 0
        
        
