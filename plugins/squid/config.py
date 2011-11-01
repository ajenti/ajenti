from ajenti.api import *
from main import *


class GeneralConfig(ModuleConfig):
    target = SquidConfig
    platform = ['debian', 'centos', 'arch', 'gentoo', 'mandriva']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/squid/squid.conf'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_file = '/usr/local/etc/squid/squid.conf'
