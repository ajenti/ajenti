from ajenti.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = FMPlugin
    platform = ['any']
    
    labels = {
        'dir': 'Initial directory'
    }
    
    dir = '/'
   
