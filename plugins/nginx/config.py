from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'nginxbackend'
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/nginx/'
   
