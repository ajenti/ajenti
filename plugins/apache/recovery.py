from ajenti.plugins.recovery.api import *

class ApacheRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Apache'
    id = 'apache'
    path = '/etc/apache2'
    
