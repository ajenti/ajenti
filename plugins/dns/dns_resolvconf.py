from ajenti.api import *
from ajenti.com import *
from ajenti.utils import *

from api import *


class ResolvConfDNSConfig(Plugin):
    implements(IDNSConfig)
    platform = ['debian', 'arch', 'freebsd', 'centos', 'fedora', 'gentoo']
    name = 'DNS'
    id = 'dns'
    
    nameservers = None

    def __init__(self):
        self.nameservers = []

        try:
            ss = ConfManager.get().load('dns', '/etc/resolv.conf')
            ss = ss.splitlines()
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
        s = ''
        for i in self.nameservers:
            s += i.cls + ' ' + i.address + '\n'
        ConfManager.get().save('dns', '/etc/resolv.conf', s)
        ConfManager.get().commit('dns')
        

class DNSConfig (Plugin):
    implements(IConfigurable)
    name = 'DNS'
    id = 'dns'
    
    def list_files(self):
        return ['/etc/resolv.conf']
    
