import os
import subprocess

from ajenti.api import *

from api import *
from nctp_linux import *


optionmap = {
    'IPADDR': 'address',
    'NETMASK': 'netmask',
    'GATEWAY': 'gateway',
    'BROADCAST': 'broadcast',
    'MACADDR': 'hwaddr',
}


@plugin
class CentosNetworkConfig (LinuxIfconfig, INetworkConfig):
    platforms = ['centos', 'mageia']

    interfaces = None

    classes = {
        'none': ('inet', 'static'),
        'dhcp': ('inet', 'dhcp'),
        'loopback': ('inet', 'loopback')
    }

    def __init__(self):
        self.rescan()

    def rescan(self):
        self.interfaces = {}

        for ifcf in os.listdir('/etc/sysconfig/network-scripts/'):
            if ifcf.startswith('ifcfg-'):
                ifcn = ifcf[6:]
                with open('/etc/sysconfig/network-scripts/' + ifcf, 'r') as f:
                    ss = f.read().splitlines()
                    d = {}
                    for s in ss:
                        try:
                            k = s.split('=', 1)[0].strip('\t "\'')
                            v = s.split('=', 1)[1].strip('\t "\'')
                            d[k] = v
                        except:
                            pass

                    m = 'loopback'
                    c = 'inet'
                    try:
                        if 'BOOTPROTO' in d:
                            m = d['BOOTPROTO']
                        c, m = self.classes[m]
                    except:
                        pass

                    e = NetworkInterface()
                    e.name = ifcn
                    self.interfaces[ifcn] = e
                    self.interfaces[ifcn].auto = 'yes' in d.get('ONBOOT', 'no')
                    e.type = c
                    e.addressing = m
                    for k in d:
                        if k == 'BOOTPROTO':
                            pass
                        elif k in optionmap:
                            e.params[optionmap[k]] = d[k]
                        else:
                            e.params[k] = d[k]

                    e.devclass = self.detect_dev_class(e)
                    try:
                        e.up = 'UP' in subprocess.check_output(['ifconfig', e.name])
                    except:
                        e.up = False
                    e.bit_classes = self.detect_iface_bits(e)

    def save(self):
        for i in self.interfaces:
            with open('/etc/sysconfig/network-scripts/ifcfg-' + i, 'w') as f:
                self.save_iface(self.interfaces[i], f)
        return

    def save_iface(self, iface, f):
        iface.params['ONBOOT'] = 'yes' if iface.auto else 'no'
        for x in self.classes:
            if self.classes[x] == (iface.type, iface.addressing):
                f.write('BOOTPROTO="' + x + '"\n')

        for x in iface.params:
            if not iface.params[x]:
                continue
            fnd = False
            for k in optionmap:
                if optionmap[k] == x:
                    f.write(k + '="' + iface.params[x] + '"\n')
                    fnd = True
            if not fnd:
                f.write(x + '="' + iface.params[x] + '"\n')
