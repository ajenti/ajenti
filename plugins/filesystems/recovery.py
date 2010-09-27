from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class FstabRecovery(RecoveryProvider):
    name = 'Filesystems'
    id = 'fstab'
    
    def backup(self, dir):
        shell('cp /etc/fstab %s/'%dir)
    
    def restore(self, dir):
        shell('cp %s/fstab /etc/fstab'%dir)
    
