from ajenti import apis
from ajenti.utils import shell
from ajenti.com import *


class LinuxSysStat(Plugin):
    implements(apis.sysstat.ISysStat)
    platform = ['debian', 'arch', 'centos', 'fedora', 'gentoo']
    
    def get_load(self):
        return open('/proc/loadavg', 'r').read().split()[0:3]
        
    def get_ram(self):
        s = shell('free -m | grep Mem').split()[1:]
        t = int(s[0])
        u = int(s[1])
        b = int(s[4])
        c = int(s[5])
        u -= c + b;
        return (u, t)

    def get_swap(self):
        s = shell('free -m | grep Swap').split()[1:]
        return (int(s[1]), int(s[0]))

