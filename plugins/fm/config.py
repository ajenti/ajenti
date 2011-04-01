from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'fmplugin'
    platform = ['any']
    
    labels = {
        'dir': 'Initial directory'
    }
    
    dir = '/'
   
