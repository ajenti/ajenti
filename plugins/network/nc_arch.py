from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

from api import *
from nctp_linux import *


class ArchNetworkConfig(LinuxIfconfig):
    implements(INetworkConfig)
    platform = ['Arch']
    
    interfaces = None
    
    
    def __init__(self):
        self.rcconf = apis.rcconf.RCConf(self.app)
        self.rescan()

    def rescan(self):
        self.interfaces = {}
        for name in self.rcconf.get_param('INTERFACES')[1:-1].split(','):
            try:
                s = self.rcconf.get_param(name).split()
            except:
                continue
            if not s:
                continue
            iface = NetworkInterface()
            iface.name = name
            self.interfaces[name] = iface
            if s[0] == 'dhcp':
                iface.type = 'inet'
                iface.addressing = 'dhcp'
            else:
                iface.type = 'inet'
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
        for iface in self.interfaces.values():
            if iface.addressing == 'dhcp':
                self.rcconf.set_param(iface.name, 'dhcp')
            else:                
                s = [iface.name, iface.params['address']]
                for k in iface.params:
                    if k != 'address':
                        s.append(k)
                        s.append(iface.params[k])
                self.rcconf.set_param(iface.name, ' '.join(s))

  
