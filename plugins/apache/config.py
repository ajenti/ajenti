from ajenti.api import *
from main import *
from main_single import *


class GeneralConfig(ModuleConfig):
    target = ApacheBackend
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/apache2'

   
class BSDConfig(GeneralConfig):
    target = ApacheBackend
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/apache2'
   
   
class SingleConfig(ModuleConfig):
    target = ApacheSingleConfigBackend
    plugin = 'apachesingleconfigbackend'
    platform = ['any']
    
    labels = {
        'cfg_file': 'Configuration file',
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_file = '/etc/httpd/conf/httpd.conf'
    cfg_path = '/etc/httpd'
   
