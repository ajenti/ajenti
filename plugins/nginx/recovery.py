from ajenti.plugins.recovery.api import *

class NginxRecovery(SimpleDirectoryRecoveryProvider):
    name = 'nginx'
    id = 'nginx'
    path = '/etc/nginx'
    
