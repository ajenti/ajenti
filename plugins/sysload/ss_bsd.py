from ajenti import apis
from ajenti.utils import shell
from ajenti.com import *


class BSDSysStat(Plugin):
    implements(apis.sysstat.ISysStat)
    platform = ['freebsd']

    def get_load(self):
        return shell('sysctl vm.loadavg').split()[2:5]

    def get_ram(self):
        s = shell("top -b | grep Mem | sed 's/[^0-9]/ /g' | awk '{print $1+$2+$3+$4+$5+$6, $1+$2+$3, $4+$5+$6}'").split()
        t = int(s[0])
        u = int(s[1])
        f = int(s[2])
        return (u, t)

    def get_swap(self):
        s = shell('top -b | grep Swap | sed "s/[^0-9]/ /g"').split()
        return (int(s[1]), int(s[0]))

