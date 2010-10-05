from ajenti.plugins.recovery.api import *


class SquidRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Squid'
    id = 'squid'
    path = '/etc/squid'
    
