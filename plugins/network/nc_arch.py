import time
import os

from ajenti.com import *
from ajenti.utils import *
from ajenti.ui import *

from api import *


class ArchNetworkConfig(Plugin):
    implements(INetworkConfig)
    platform = ['Arch']

    interfaces = None
    nameservers = None

    def __init__(self):
        self.rescan()

    def rescan(self):
        self.interfaces = {}
        self.nameservers = []

        rcconf = open('/etc/rc.conf').read().split('\n')
        autos = []
        for line in rcconf:
            if line.startswith('INTERFACES=('):
                autos = line[line.index('(')+1:][:-1].split(',')
            if line.startswith('eth'):
                try:
                    m = 'static'
                    c = 'inet'
                    n = line.split('=')[0]
                    
                    line = line[(line.index('"')+1):]
                    line = line[:(line.index('"'))]
                    params = line.split()
                    
                    if params[0] != 'dhcp':
                       n = params[0]
                    e = self.get_iface(n, ['linux-basic', 'linux-ipv4'])
                    e.name = n
                    e.mode = 'dhcp' if 'dhcp' in params else 'static'
                    e.cls = 'inet'
                    e.clsname = self.detect_iface_class_name(e.name)
                    e.up = (shell_status('ifconfig ' + e.name + '|grep UP') == 0)
                    if e.up:
                        e.addr = shell('ifconfig ' + e.name + ' | grep \'inet addr\' | awk \'{print $2}\' | tail -c+6')
                        
                    if params[0] != 'dhcp':
                        e.params['address'] = params[1]
                        i = 2
                        while i < len(params):
                            e.params[params[i]] = params[i+1]
                            i += 2
                except Exception, e:
                    e.print_stack()

        for ifc in self.interfaces:
            self.interfaces[ifc].auto = ifc in autos
            
        # Load DNS servers
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
        rcconf = open('/etc/rc.conf').read().split('\n')
        idx = 0
        insidx = -1
        while idx < len(rcconf):
            if rcconf[idx].startswith('eth'): # Drop interfaces
                rcconf.pop(idx)
            elif rcconf[idx].startswith('INTERFACES'): # Place for new config
                rcconf.pop(idx)
                insidx = idx
            else:
                idx += 1
                
        f = open('/etc/rc.conf', 'w')
        f.write('\n'.join(rcconf[0:insidx]) + '\n')
        ifcline = 'INTERFACES=('
        autos = []
        for i in self.interfaces:
            self.interfaces[i].save(f)
            if self.interfaces[i].auto:
                autos.append(i)
        ifcline += ','.join(autos) + ')\n'
        f.write(ifcline)
        f.write('\n'.join(rcconf[insidx:]))
        f.close()
        
        f = open('/etc/resolv.conf', 'w')
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
        p = ''
        if self.mode == 'dhcp':
            p = 'dhcp'
        else:
            p = '%s %s netmask %s broadcast %s' % \
                (self.name,
                self.params['address'], 
                self.params['netmask'], 
                self.params['broadcast'])
        s = '%s="%s"\n' % (self.name, p)
        f.write(s)


class Nameserver(NameserverBase):
    pass
