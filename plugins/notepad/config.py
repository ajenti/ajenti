from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'notepadplugin'
    platform = ['any']
    
    labels = {
        'dir': 'Initial directory'
    }
    
    dir = '/etc'
   
