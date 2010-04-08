from ajenti.com import *
from api import *

class UbuntuNetworkConfig(Plugin):
    implements(INetworkConfig)

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

        while len(ss)>0:
            if (len(ss[0]) > 0 and not ss[0][0] == '#'):
                a = ss[0].strip(' \t\n').split(' ')
                for s in a:
                    if s == '': a.remove(s)
                if (a[0] == 'auto'):
                    auto.append(a[1])
                elif (a[0] == 'iface'):
                    e = self.get_iface(a[1], self.detect_iface_class(a))
                    e.cls = a[2]
                    e.mode = a[3]
                else:
                    e.params[a[0]] = ' '.join(a[1:])
            if (len(ss)>1): ss = ss[1:]
            else: ss = []

        for x in auto:
            self.interfaces[x].auto = True

    def get_iface(self, name, cls):
        if not self.interfaces.has_key(name):
            self.interfaces[name] = NetworkInterface(self.app)
            for x in cls:
                b = self.app.grab_plugins(INetworkConfigBit,
                        lambda p: p.cls == x)[0]
                b.iface = self.interfaces[name]
                self.interfaces[name].bits.append(b)

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

    def get_text(self): return 'ubuntu!'



class NetworkInterface(Plugin):
    multi_instance = True

    cls = 'unknown'
    mode = 'static'
    params = None
    auto = False
    name = 'unknown'
    bits = None

    def __init__(self):
        self.params = {}
        self.bits = []

"""	def save(self):
		f = open('/etc/network/interfaces', 'w')
		for i in self.interfaces.keys():
			self.interfaces[i].save(f)
		f.close()
		return"""
