import time

from ajenti.com import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.uzuri_common import ClusteredConfig

from api import *
from nctp_ifconfig import *


class DebianNetworkConfig(LinuxIfconfig, ClusteredConfig):
    implements(INetworkConfig)
    platform = ['Debian', 'Ubuntu']
    name = 'Network'
    id = 'network'
    files = [('/etc/network', '*')] 
    run_after = ['/etc/init.d/networking restart']
    
    interfaces = None
    nameservers = None

    def __init__(self):
        self.rescan()

    def rescan(self):
        self.interfaces = {}

        # Load interfaces
        try:
            f = self.open('/etc/network/interfaces')
            ss = f.read().splitlines()
            f.close()
        except IOError, e:
            return

        auto = []

        while len(ss)>0:
            if (len(ss[0]) > 0 and not ss[0][0] == '#'):
                a = ss[0].strip(' \t\n').split(' ')
                for s in a:
                    if s == '': a.remove(s)
                if (a[0] == 'auto'):
                    auto.append(a[1])
                elif (a[0] == 'allow-hotplug'):
                    pass
#                    hotplug.append(a[1])
                elif (a[0] == 'iface'):
                    tmp = NetworkInterface()
                    tmp.addressing = a[3]
                    tmp.type = a[2]
                    e = self.get_iface(a[1], self.detect_iface_bits(tmp))
                    del tmp
                    e.type = a[2]
                    e.addressing = a[3]
                    e.devclass = self.detect_dev_class(e)
                    e.up = (shell_status('ifconfig ' + e.name + '|grep UP') == 0)
                else:
                    e.params[a[0]] = ' '.join(a[1:])
            if (len(ss)>1): ss = ss[1:]
            else: ss = []

        for x in auto:
            self.interfaces[x].auto = True


    def get_iface(self, name, bits):
        if not self.interfaces.has_key(name):
            self.interfaces[name] = NetworkInterface()
            for x in bits:
                try:
                    b = self.app.grab_plugins(INetworkConfigBit,\
                            lambda p: p.cls == x)[0]
                    b.iface = self.interfaces[name]
                    self.interfaces[name].bits.append(b)
                except:
                    pass

        self.interfaces[name].name = name
        return self.interfaces[name]


    def save(self):
        f = self.open('/etc/network/interfaces', 'w')
        for i in self.interfaces:
            self.save_iface(self.interfaces[i], f)
        f.close()
        return

    def save_iface(self, iface, f):
        if iface.auto:
            f.write('auto ' + iface.name + '\n')
        f.write('iface %s %s %s\n' % (iface.name,iface.type,iface.addressing))
        for x in iface.params:
            f.write('\t%s %s\n' % (x,iface.params[x]))
        f.write('\n')
