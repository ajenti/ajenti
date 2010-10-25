from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'apachebackend'
    platform = ['any']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/apache2'
   
