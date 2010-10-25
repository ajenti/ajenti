from ajenti import apis
from ajenti.utils import shell
from ajenti.com import *


class BSDSysStat(Plugin):
    implements(apis.sysstat.ISysStat)
    platform = ['freebsd']
    
    def get_load(self):
        return shell('sysctl vm.loadavg').split()[2:5]
        
    def get_ram(self):
        s = shell('freecolor -om | grep Mem').split()[1:]
        t = int(s[0])
        u = int(s[1])
        b = int(s[4])
        c = int(s[5])
        u -= c + b;
        return (u, t)

    def get_swap(self):
        s = shell('freecolor -om | grep Swap').split()[1:]
        return (int(s[1]), int(s[0]))

