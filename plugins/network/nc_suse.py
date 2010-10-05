import time
import os

from ajenti.com import *
from ajenti.utils import *
from ajenti.ui import *

from api import *

from ajenti.plugins.uzuri_common import ClusteredConfig


optionmap = {
    'IPADDR': 'address',
    'NETMASK': 'netmask',
    'BROADCAST': 'broadcast',
    'MTU': 'mtu',
    'LLADDR': 'hwaddr',
    'PRE_UP_SCRIPT': 'pre-up',
    'PRE_DOWN_SCRIPT': 'pre-DOWN',
    'POST_UP_SCRIPT': 'post-up',
    'POST_DOWN_SCRIPT': 'post-down',
    'REMOTE_IPADDR': 'pointopoint'
}

class SuseNetworkConfig(ClusteredConfig):
    implements(INetworkConfig)
    platform = ['openSUSE']
    name = 'Network'
    id = 'network'
    files = [('/etc/sysconfig/network', '*'), ('/etc', 'resolv.conf')] 
    run_after = ['/etc/init.d/network restart']

    interfaces = None
    nameservers = None

    classes = {
        'static': ('inet', 'static'),
        '6to4': ('inet6', 'static'),
        'dhcp': ('inet', 'dhcp'),
        'loopback': ('inet', 'loopback')
    }

    def __init__(self):
        self.rescan()

    def rescan(self):
        self.interfaces = {}
        self.nameservers = []

        for ifcf in os.listdir(self.root()+'/etc/sysconfig/network/'):
            if ifcf.startswith('ifcfg-'):
                ifcn = ifcf[6:]
                with self.open('/etc/sysconfig/network/' + ifcf, 'r') as f:
                    ss = f.read().splitlines()
                    d = {}
                    for s in ss:
                        try:
                            k = s.split('=')[0].strip('\t \'');
                            v = s.split('=')[1].strip('\t \'');
                            d[k] = v
                        except:
                            pass

                    m = 'loopback'
                    c = 'inet'
                    try:
                        if 'BOOTPROTO' in d:
                            m = d['BOOTPROTO']
                        c,m = self.modes[m]
                    except:
                        pass

                    e = self.get_iface(ifcn, self.detect_iface_class(ifcn, c, m))
                    e.name = ifcn
                    e.mode = m
                    e.cls = c
                    for k in d:
                        if k == 'STARTMODE':
                            e.auto = d[k] == 'auto' or d[k] =='hotplug'
                            e.hotplug = d[k] =='hotplug'
                        elif k == 'BOOTPROTO':
                            pass
                        elif k in optionmap:
                            e.params[optionmap[k]] = d[k]
                        else:
                            e.params[k] = d[k]

                    e.clsname = self.detect_iface_class_name(e.name)
                    e.up = (shell_status('ifconfig ' + e.name + '|grep UP') == 0)
                    if e.up:
                        e.addr = shell('ifconfig ' + e.name + ' | grep \'inet addr\' | awk \'{print $2}\' | tail -c+6')

        # Load DNS servers
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

    def get_iface(self, name, cls):
        if not self.interfaces.has_key(name):
            self.interfaces[name] = SuseNetworkInterface()
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

    def detect_iface_class(self, n, c, m):
        r = ['linux-basic']
        if c == 'inet' and m == 'static':
            r.append('linux-ipv4')
        if c == 'inet6' and m == 'static':
            r.append('linux-ipv6')
        if n == 'ppp':
            r.append('linux-ppp')
        if n == 'wlan':
            r.append('linux-wlan')
        if n == 'ath':
            r.append('linux-wlan')
        if n == 'ra':
            r.append('linux-wlan')
        if n == 'br':
            r.append('linux-bridge')
        if n == 'tun':
            r.append('linux-tunnel')

        r.append('linux-ifupdown')
        return r

    def detect_iface_class_name(self, n):
        if n[:-1] in ['ppp', 'wvdial']:
            return 'PPP'
        if n[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
            return 'Wireless'
        if n[:-1] == 'br':
            return 'Bridge'
        if n[:-1] == 'tun':
            return 'Tunnel'
        if n == 'lo':
            return 'Loopback'
        if n[:-1] == 'eth':
            return 'Ethernet'

        return 'Unknown'

    def save(self):
        for i in self.interfaces:
            with self.open('/etc/sysconfig/network/ifcfg-' + i, 'w') as f:
                self.interfaces[i].save(f)

        f = self.open('/etc/resolv.conf', 'w')
        for i in self.nameservers:
            f.write(i.cls + ' ' + i.address + '\n')
        f.close()
        return

    def ns_edit_dialog(self, ns):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Type:'),
                    UI.Select(
                        UI.SelectOption(text='Nameserver', value='nameserver', selected=(ns.cls=='nameserver')),
                        UI.SelectOption(text='Local domain', value='domain', selected=(ns.cls=='domain')),
                        UI.SelectOption(text='Search list', value='search', selected=(ns.cls=='search')),
                        UI.SelectOption(text='Sort list', value='sortlist', selected=(ns.cls=='sortlist')),
                        UI.SelectOption(text='Options', value='options', selected=(ns.cls=='options')),
                        name='cls'
                    ),
                UI.LayoutTableRow(
                    UI.Label(text='Value:'),
                    UI.TextInput(name='address', value=ns.address),
                    )
                )
            )
        return p

    def new_iface(self):
        return NetworkInterface()

    def new_nameserver(self):
        return Nameserver()

    def up(self, iface):
        shell('ifconfig %s up' % iface.name)
        time.sleep(1)
        self.rescan()

    def down(self, iface):
        shell('ifconfig %s down' % iface.name)
        time.sleep(1)
        self.rescan()


class SuseNetworkInterface(NetworkInterfaceBase):
    cls = 'unknown'
    mode = 'static'
    params = None
    auto = False
    hotplug = False

    classes = {
        ('inet', 'static'): 'static',
        ('inet6', 'static'): '6to4',
        ('inet', 'dhcp'): 'dhcp',
        ('inet', 'loopback'): 'loopback'
    }

    def __init__(self):
        NetworkInterfaceBase.__init__(self)
        self.params = {}

    def __getitem__(self, idx):
        if self.params.has_key(idx):
            return self.params[idx]
        else:
            return ''

    def __setitem__(self, idx, val):
        if idx in ['auto', 'mode', 'action', 'hotplug']: return
        self.params[idx] = val

    def save(self, f):
        if self.hotplug:
            f.write('STARTMODE=\'hotplug\'\n')
        elif self.auto:
            f.write('STARTMODE=\'auto\'\n')
        elif self.name == 'lo':
            f.write('STARTMODE=\'onboot\'\n')
        else:
            f.write('STARTMODE=\'manual\'\n')

        for x in self.classes:
            if x == (self.cls, self.mode):
                f.write('BOOTPROTO=\'' + self.classes[x] + '\'\n');

        for x in self.params:
            fnd = False
            for k in optionmap:
                if optionmap[k] == x:
                    f.write(k + '=\'' + self.params[x] + '\'\n')
                    fnd = True
            if not fnd:
                f.write(x + '=\'' + self.params[x] + '\'\n')


class Nameserver(NameserverBase):
    pass
