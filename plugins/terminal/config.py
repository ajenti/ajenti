from ajenti.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = TerminalPlugin
    platform = ['any']
    
    labels = {
        'shell': 'Shell'
    }
    
    shell = 'su'
