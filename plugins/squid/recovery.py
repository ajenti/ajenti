from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class SquidRecovery(RecoveryProvider):
    name = 'Squid'
    id = 'squid'
    
    def backup(self, dir):
        shell('cp /etc/squid/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/squid/*')
        shell('cp %s/* /etc/squid/'%dir)
    
