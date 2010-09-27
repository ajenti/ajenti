from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class SambaRecovery(RecoveryProvider):
    name = 'Firewall'
    id = 'iptables'
    
    def backup(self, dir):
        shell('cp /etc/iptables.up.rules %s/'%dir)
    
    def restore(self, dir):
        shell('cp %s/iptables.up.rules /etc/iptables.up.rules'%dir)
    
