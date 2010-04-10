from ajenti.com import *
from api import *
from ajenti.utils import *

class DebianNetworkConfig(Plugin):
    implements(INetworkConfig)
    platform = ['Debian', 'Ubuntu']

    interfaces = None

    def __init__(self):
        self.interfaces = {}

        try:
            f = open('/etc/network/interfaces')
            ss = f.read().splitlines()
            f.close()
        except IOError, e:
            return

        auto = []
        hotplug = []

        while len(ss)>0:
            if (len(ss[0]) > 0 and not ss[0][0] == '#'):
                a = ss[0].strip(' \t\n').split(' ')
                for s in a:
                    if s == '': a.remove(s)
                if (a[0] == 'auto'):
                    auto.append(a[1])
                elif (a[0] == 'allow-hotplug'):
                    hotplug.append(a[1])
                elif (a[0] == 'iface'):
                    e = self.get_iface(a[1], self.detect_iface_class(a))
                    e.cls = a[2]
                    e.mode = a[3]
                    e.clsname = self.detect_iface_class_name(a)
                    e.up = (shell_status('ifconfig ' + e.name + '|grep UP') == 0)
                    if e.up:
                        e.addr = shell('ifconfig ' + e.name + ' | grep \'inet addr\' | awk \'{print $2}\' | tail -c+6')
                else:
                    e.params[a[0]] = ' '.join(a[1:])
            if (len(ss)>1): ss = ss[1:]
            else: ss = []

        for x in auto:
            self.interfaces[x].auto = True
        for x in hotplug:
            self.interfaces[x].hotplug = True
            

    def get_iface(self, name, cls):
        if not self.interfaces.has_key(name):
            self.interfaces[name] = NetworkInterface(self.app)
            for x in cls:
		try:
                    b = self.app.grab_plugins(INetworkConfigBit,
                            lambda p: p.cls == x)[0]
                    b.iface = self.interfaces[name]
                    self.interfaces[name].bits.append(b)
                except:
                    pass

        self.interfaces[name].name = name
        return self.interfaces[name]

    def detect_iface_class(self, a):
        r = ['linux-basic']
        if a[2] == 'inet' and a[3] == 'static':
            r.append('linux-ipv4')
        if a[2] == 'inet6' and a[3] == 'static':
            r.append('linux-ipv6')
        if a[1][:-1] == 'ppp':
            r.append('linux-ppp')
        if a[1][:-1] == 'wlan':
            r.append('linux-wlan')
        if a[1][:-1] == 'ath':
            r.append('linux-wlan')
        if a[1][:-1] == 'ra':
            r.append('linux-wlan')
        if a[1][:-1] == 'br':
            r.append('linux-bridge')
        if a[1][:-1] == 'tun':
            r.append('linux-tunnel')

        r.append('linux-ifupdown')
        return r

    def detect_iface_class_name(self, a):
        if a[1][:-1] in ['ppp', 'wvdial']:
            return 'PPP'
        if a[1][:-1] in ['wlan', 'ra', 'wifi', 'ath']:
            return 'Wireless'
        if a[1][:-1] == 'br':
            return 'Bridge'
        if a[1][:-1] == 'tun':
            return 'Tunnel'
        if a[1] == 'lo':
            return 'Loopback'
        if a[1][:-1] == 'eth':
            return 'Ethernet'

        return 'Unknown'

    def save(self):
        f = open('/etc/network/interfaces', 'w')
        for i in self.interfaces:
            self.interfaces[i].save(f)
        f.close()
        return


class NetworkInterface(Plugin):
    multi_instance = True

    cls = 'unknown'
    clsname = ''
    up = False
    addr = ''
    mode = 'static'
    params = None
    auto = False
    hotplug = False
    name = 'unknown'
    bits = None

    def __init__(self):
        self.params = {}
        self.bits = []

    def __getitem__(self, idx):
        if self.params.has_key(idx):
            return self.params[idx]
        else:
            return ''

    def __setitem__(self, idx, val):
        if idx in ['auto', 'mode', 'action', 'hotplug']: return
        self.params[idx] = val

    def save(self, f):
        if self.auto:
            f.write('auto ' + self.name + '\n')
        if self.hotplug:
            f.write('allow-hotplug ' + self.name + '\n')
        f.write('iface ' + self.name + ' ' + self.cls + ' ' + self.mode + '\n')
        for x in self.params:
            f.write('\t' + x + ' ' + self.params[x] + '\n')
        f.write('\n')
