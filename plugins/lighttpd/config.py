from ajenti.api import *
from main import *


class GeneralConfig(ModuleConfig):
    target = LighttpdBackend
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/lighttpd/'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    
    platform = ['freebsd']

    cfg_dir = '/usr/local/etc/lighttpd'
