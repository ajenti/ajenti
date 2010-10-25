from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'squidconfig'
    platform = ['any']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/squid/squid.conf'
   
