from ajenti.plugins.recovery.api import *


class DNSRecovery(SimpleFileRecoveryProvider):
    name = 'DNS'
    id = 'dns'
    path = '/etc/resolv.conf'
    
