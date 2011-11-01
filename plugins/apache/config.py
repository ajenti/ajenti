from ajenti.api import *
from main import *
from main_single import *


class GeneralConfig(ModuleConfig):
    target = ApacheBackend
    platform = ['debian', 'arch']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/apache2'

   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_dir = '/usr/local/etc/apache2'
   
   
class SingleConfigGeneral(ModuleConfig):
    target = ApacheSingleConfigBackend
    platform = ['centos', 'mandriva']
    
    labels = {
        'cfg_file': 'Configuration file',
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_file = '/etc/httpd/conf/httpd.conf'
    cfg_dir = '/etc/httpd'
   
   
class SingleConfigBSD(SingleConfigGeneral):
    platform = ['freebsd']
    
    cfg_file = '/usr/local/etc/apache22/httpd.conf'
    cfg_dir = '/usr/local/etc/apache22'
   
