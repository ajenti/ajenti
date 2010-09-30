from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class SambaRecovery(RecoveryProvider):
    name = 'Samba'
    id = 'samba'
    
    def backup(self, dir):
        shell('cp /etc/samba/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/samba/*')
        shell('cp %s/* /etc/samba/'%dir)
    
