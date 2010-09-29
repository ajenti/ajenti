from ajenti.plugins.recovery.api import *


class DebianNetworkRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Network'
    id = 'network'
    platform = ['Debian', 'Ubuntu']
    path = '/etc/network'
    
    
class SuseNetworkRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Network'
    id = 'network'
    platform = ['openSUSE']
    path = '/etc/sysconfig/network'
