from ajenti.plugins.recovery.api import *


class FstabRecovery(SimpleFileRecoveryProvider):
    name = 'Filesystems'
    id = 'fstab'
    path = '/etc/fstab'
    
