from ajenti.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = RecoveryPlugin
    
    labels = {
        'auto': 'Automatic backup'
    }
    
    auto = True
   
