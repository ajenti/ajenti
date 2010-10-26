from ajenti.plugins.recovery.api import *

class UsersRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Apache'
    id = 'apache'
    path = '/etc/apache2'
    
