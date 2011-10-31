from ajenti.api import *
from main import *
from main_single import *


class GeneralConfig(ModuleConfig):
    target = NginxBackend
    platform = ['debian', 'arch']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/nginx/'
   
   
class BSDConfig(ModuleConfig):
    target = NginxSingleConfigBackend
    platform = ['freebsd']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/usr/local/etc/nginx/nginx.conf'
   

class GeneralSCConfig(BSDConfig):
    target = NginxSingleConfigBackend
    platform = ['gentoo', 'centos']
    
    cfg_file = '/etc/nginx/nginx.conf'


class ArchConfig(BSDConfig):
    target = NginxSingleConfigBackend
    platform = ['arch']
    
    cfg_file = '/etc/nginx/conf/nginx.conf'