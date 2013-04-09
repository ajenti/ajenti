import re
import os

from ajenti.api import *
from ajenti.utils import *
from ajenti.com import *
from ajenti import apis


class Host:
    def __init__(self):
        self.ip = '';
        self.name = '';
        self.aliases = '';


class Config(Plugin):
    implements(IConfigurable)
    name = 'Hosts'
    icon = '/dl/hosts/icon.png'
    id = 'hosts'

    def list_files(self):
        return ['/etc/hosts']

    def read(self):
        ss = ConfManager.get().load('hosts', '/etc/hosts').split('\n')
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

    def save(self, hh):
        d = ''
        for h in hh:
            d += '%s\t%s\t%s\n' % (h.ip, h.name, h.aliases)
        ConfManager.get().save('hosts', '/etc/hosts', d)
        ConfManager.get().commit('hosts')

    def gethostname(self):
        return self.app.get_backend(IHostnameManager).gethostname()

    def sethostname(self, hn):
        self.app.get_backend(IHostnameManager).sethostname(hn)



class IHostnameManager(Interface):
    def gethostname(self):
        pass

    def sethostname(self, hn):
        pass


class LinuxGenericHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['debian']

    def gethostname(self):
        return open('/etc/hostname').read()

    def sethostname(self, hn):
        open('/etc/hostname', 'w').write(hn)


class ArchHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['arch']

    def gethostname(self):
        return open('/etc/hostname').read()

    def sethostname(self, hn):
        open('/etc/hostname', 'w').write(hn)


class BSDHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['freebsd']

    def gethostname(self):
        return apis.rcconf.RCConf(self.app).get_param('hostname')

    def sethostname(self, hn):
        apis.rcconf.RCConf(self.app).set_param('hostname', hn, near='hostname')


class CentOSHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['centos', 'fedora', 'mandriva']

    def gethostname(self):
        rc = apis.rcconf.RCConf(self.app)
        rc.file = '/etc/sysconfig/network'
        return rc.get_param('HOSTNAME')

    def sethostname(self, hn):
        rc = apis.rcconf.RCConf(self.app)
        rc.file = '/etc/sysconfig/network'
        rc.set_param('HOSTNAME', hn, near='HOSTNAME')


class GentooHostnameManager(Plugin):
    implements(IHostnameManager)
    platform = ['gentoo']

    def gethostname(self):
        rc = apis.rcconf.RCConf(self.app)
        rc.file = '/etc/conf.d/hostname'
        return rc.get_param('hostname')

    def sethostname(self, hn):
        rc = apis.rcconf.RCConf(self.app)
        rc.file = '/etc/conf.d/hostname'
        rc.set_param('hostname', hn, near='hostname')
        
