from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class SARGRecovery(RecoveryProvider):
    name = 'SARG'
    id = 'sarg'
    
    def backup(self, dir):
        shell('cp /etc/sarg/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/sarg/*')
        shell('cp %s/* /etc/sarg/'%dir)
    
