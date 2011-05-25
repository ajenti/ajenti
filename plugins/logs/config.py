from ajenti.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = LogsPlugin
    platform = ['any']
    
    labels = {
        'dir': 'Log directory'
    }
    
    dir = '/var/log'
   
