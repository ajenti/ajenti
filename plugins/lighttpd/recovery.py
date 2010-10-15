from ajenti.plugins.recovery.api import *

class LighttpdRecovery(SimpleDirectoryRecoveryProvider):
    name = 'lighttpd'
    id = 'lighttpd'
    path = '/etc/lighttpd'
    
