from ajenti.plugins.recovery.api import *


class FirewallRecovery(SimpleFileRecoveryProvider):
    name = 'Firewall'
    id = 'iptables'
    path = '/etc/iptables.up.rules'
    
