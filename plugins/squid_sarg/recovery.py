from ajenti.plugins.recovery.api import *


class SARGRecovery(SimpleDirectoryRecoveryProvider):
    name = 'SARG'
    id = 'sarg'
    path = '/etc/sarg'
    
