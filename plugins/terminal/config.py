from ajenti.api import ModuleConfig


class GeneralConfig(ModuleConfig):
    plugin = 'terminalplugin'
    platform = ['any']
    
    labels = {
        'shell': 'Shell'
    }
    
    shell = '/bin/sh -c $SHELL'
   
