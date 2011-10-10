from ajenti.api import *
from ajenti.utils import *
from ajenti.com import *


class Host:
    def __init__(self):
        self.ip = '';
        self.name = '';
        self.aliases = '';


class Config(Plugin):
    implements(IConfigurable)
    name = 'My Hosts'
    icon = '/dl/myhosts/icon.png'
    id = 'myhosts'

    def list_files(self):
        return ['/etc/hosts']

    def read(self):
        ss = ConfManager.get().load('myhosts', '/etc/hosts').split('\n')
        r = []

        for s in ss:
            if s != '' and s[0] != '#':
                try:
                    s = s.split()
                    h = Host()
                    try:
                        h.ip = s[0]
                        h.name = s[1]
                        for i in range(2, len(s)):
                            h.aliases += '%s ' % s[i]
                        h.aliases = h.aliases.rstrip();
                    except:
                        pass
                    r.append(h)
                except:
                    pass

        return r

    def save(self, hosts):
        d = ''
        for h in hosts:
            d += '%s\t%s\t%s\n' % (h.ip, h.name, h.aliases)
        ConfManager.get().save('myhosts', '/etc/hosts', d)
        ConfManager.get().commit('myhosts')
