from ajenti.api import *


class GeneralConfig(ModuleConfig):
    plugin = 'squidconfig'
    platform = ['any']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/squid/squid.conf'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/squid/squid.conf'
