from ajenti.com import *
from ajenti.utils import *

from api import *


class ResolvConfDNSConfig(Plugin):
    implements(IDNSConfig)
    platform = ['debian', 'opensuse', 'arch', 'freebsd', 'centos', 'fedora']
    name = 'DNS'
    id = 'dns'
    
    nameservers = None

    def __init__(self):
        self.nameservers = []

        try:
            f = open('/etc/resolv.conf')
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
        f = open('/etc/resolv.conf', 'w')
        for i in self.nameservers:
            f.write(i.cls + ' ' + i.address + '\n')
        f.close()
        return

