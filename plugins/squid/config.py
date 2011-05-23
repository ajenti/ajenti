from ajenti.api import *
from main import *


class GeneralConfig(ModuleConfig):
    plugin = SquidConfig
    platform = ['any']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/squid/squid.conf'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/squid/squid.conf'
