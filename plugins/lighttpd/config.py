from ajenti.api import *


class GeneralConfig(ModuleConfig):
    plugin = 'lighttpdbackend'
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/lighttpd/'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/lighttpd'
