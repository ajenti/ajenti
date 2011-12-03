from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

from api import *
from nctp_linux import *

rc_net_keys = ('address', 'netmask', 'broadcast', 'gateway')

class ArchNetworkConfig(LinuxIfconfig):
    implements(INetworkConfig)
    platform = ['Arch']
    
    interfaces = None
    
    def __init__(self):
        self.rcconf = apis.rcconf.RCConf(self.app)
        self.rescan()
    
    def rescan(self):
        self.interfaces = {}
        name = self.rcconf.get_param('interface')
        
        if name == '':
            return
        
        iface = NetworkInterface()
        iface.name = name
        iface.type = 'inet'
        iface.auto = True
        self.interfaces[name] = iface
        
        for key in rc_net_keys:
            value = self.rcconf.get_param(key)
            if key == 'address':
                iface.addressing = 'dhcp' if value == '' else 'static'
            iface.params[key] = value
        
        iface.devclass = self.detect_dev_class(iface)
        iface.up = shell_status('ifconfig ' + iface.name + '|grep UP') == 0
        iface.get_bits(self.app, self.detect_iface_bits(iface))
    
    def save(self):
        for iface in self.interfaces.values():
            for key in rc_net_keys:
                value = iface.params[key]
                if iface.addressing == 'dhcp':
                    value = ''
                self.rcconf.set_param(key, value, near='interface')