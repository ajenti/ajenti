from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'lighttpdbackend'
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/lighttpd/'
   
