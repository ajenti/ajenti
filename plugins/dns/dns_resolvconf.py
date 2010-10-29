from ajenti.com import *
from ajenti.utils import *

from api import *

from ajenti.plugins.uzuri_common import ClusteredConfig


class ResolvConfDNSConfig(ClusteredConfig):
    implements(IDNSConfig)
    platform = ['Debian', 'Ubuntu', 'openSUSE', 'Arch', 'freebsd', 'centos', 'fedora']
    name = 'DNS'
    id = 'dns'
    files = [('/etc', 'resolv.conf')] 
    
    nameservers = None

    def __init__(self):
        self.nameservers = []

        try:
            f = self.open('/etc/resolv.conf')
            ss = f.read().splitlines()
            f.close()
        except IOError, e:
            return

        for s in ss:
            if len(s) > 0:
                if s[0] != '#':
                    s = s.split(' ')
                    ns = Nameserver()
                    ns.cls = s[0]
                    ns.address = ' '.join(s[1:])
                    self.nameservers.append(ns)

    def save(self):
        f = self.open('/etc/resolv.conf', 'w')
        for i in self.nameservers:
            f.write(i.cls + ' ' + i.address + '\n')
        f.close()
        return

