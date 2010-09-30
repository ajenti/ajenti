from ajenti.plugins.recovery.api import *


class SambaRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Samba'
    id = 'samba'
    path = '/etc/samba'
    
