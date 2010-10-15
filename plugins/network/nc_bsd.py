from ajenti.com import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.uzuri_common import ClusteredConfig
from ajenti import apis

from api import *
from nctp_bsd import *


class BSDNetworkConfig(BSDIfconfig, ClusteredConfig):
    implements(INetworkConfig)
    platform = ['FreeBSD']
    name = 'Network'
    id = 'network'
    run_after = ['/etc/rc.d/netif restart']
    
    interfaces = None

    def __init__(self):
        self.rcconf = apis.rcconf.RCConf(self.app)
        self.rescan()

    def rescan(self):
        self.interfaces = {}

        for name in shell('ifconfig -l').split():
            try:
                s = self.rcconf.get_param('ifconfig_'+name).split()
            except:
                continue

            iface = NetworkInterface()
            iface.name = name
            iface.auto = s[-1] != 'NOAUTO'
            self.interfaces[name] = iface
            if not iface.auto:
                s = s[:-1]
                
            if s[0] == 'DHCP':
                iface.type = 'inet'
                iface.addressing = 'dhcp'
            if s[0] in ['inet', 'inet6']:
                iface.type = s[0]
                iface.addressing = 'static'
                iface.params['address'] = s[1]
                s = s[2:]
                while len(s)>0:
                    iface.params[s[0]] = s[1]
                    s = s[2:]
                    
            iface.devclass = self.detect_dev_class(iface)
            iface.up = shell_status('ifconfig ' + iface.name + '|grep UP') == 0
            iface.get_bits(self.app, self.detect_iface_bits(iface))

    def save(self):
        for i in self.interfaces:
            self.rcconf.set_param(
                'ifconfig_'+i, 
                self.save_iface(self.interfaces[i]), 
                near='ifconfig'
            )

    def save_iface(self, iface):
        s = []
        if iface.addressing == 'dhcp':
            s.append('DHCP')
        else:
            s.append(iface.type)
            s.append(iface.params['address'])
            for k in iface.params:
                if k != 'address':
                    s.append(k)
                    s.append(iface.params[k])
        if not iface.auto:
            s.append('NOAUTO')
        return ' '.join(s)
        