from ajenti.api import ModuleConfig
from main import RecoveryPlugin


class GeneralConfig(ModuleConfig):
    target = RecoveryPlugin
    
    labels = {
        'auto': 'Automatic backup'
    }
    
    auto = True
   
