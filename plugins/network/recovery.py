from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class DebianNetworkRecovery(RecoveryProvider):
    name = 'Network'
    id = 'network'
    platform = ['Debian', 'Ubuntu']
    
    def backup(self, dir):
        shell('cp /etc/network/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/network/*')
        shell('cp %s/* /etc/network/'%dir)
    
    
class SuseNetworkRecovery(RecoveryProvider):
    name = 'Network'
    id = 'network'
    platform = ['openSUSE']
    
    def backup(self, dir):
        shell('cp /etc/sysconfig/network/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/sysconfig/network/*')
        shell('cp %s/* /etc/sysconfig/network/'%dir)
        
