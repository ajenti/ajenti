from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'logsplugin'
    platform = ['any']
    
    labels = {
        'dir': 'Log directory'
    }
    
    dir = '/var/log'
   