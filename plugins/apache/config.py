from ajenti.api import *


class GeneralConfig(ModuleConfig):
    plugin = 'apachebackend'
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/apache2'

   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/apache2'
   
   
class SingleConfig(ModuleConfig):
    plugin = 'apachesingleconfigbackend'
    platform = ['any']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/apache2/httpd.conf'
   
