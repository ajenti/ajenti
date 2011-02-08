import time
import os

from ajenti.com import *
from ajenti.utils import *
from ajenti.ui import *

from api import *
from nctp_linux import *


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

class SuseNetworkConfig(LinuxIfconfig):
    implements(INetworkConfig)
    platform = ['openSUSE']

    interfaces = None

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

        for ifcf in os.listdir('/etc/sysconfig/network/'):
            if ifcf.startswith('ifcfg-'):
                ifcn = ifcf[6:]
                with open('/etc/sysconfig/network/' + ifcf, 'r') as f:
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
                        c,m = self.classes[m]
                    except:
                        pass

                    e = NetworkInterface()
                    e.name = ifcn
                    self.interfaces[ifcn] = e
                    e.type = c
                    e.addressing = m
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

                    e.devclass = self.detect_dev_class(e)
                    e.up = shell_status('ifconfig ' + e.name + '|grep UP') == 0
                    e.get_bits(self.app, self.detect_iface_bits(e))

       
    def save(self):
        for i in self.interfaces:
            with open('/etc/sysconfig/network/ifcfg-' + i, 'w') as f:
                self.save_iface(self.interfaces[i], f)
        return

    
    def save_iface(self, iface, f):
        if iface.name == 'lo':
            f.write('STARTMODE=\'onboot\'\n')
        elif iface.hotplug:
            f.write('STARTMODE=\'hotplug\'\n')
        elif iface.auto:
            f.write('STARTMODE=\'auto\'\n')
        else:
            f.write('STARTMODE=\'manual\'\n')        
            
        for x in self.classes:
            if x == (iface.type, iface.addressing):
                f.write('BOOTPROTO=\'' + self.classes[x] + '\'\n');

        for x in iface.params:
            fnd = False
            for k in optionmap:
                if optionmap[k] == x:
                    f.write(k + '=\'' + iface.params[x] + '\'\n')
                    fnd = True
            if not fnd:
                f.write(x + '=\'' + iface.params[x] + '\'\n')
