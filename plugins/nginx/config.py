from ajenti.api import *
from main import *


class GeneralConfig(ModuleConfig):
    target = NginxBackend
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/nginx/'
   
   
class BSDConfig(GeneralConfig):
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/nginx'
   
