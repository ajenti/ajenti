from ajenti.plugins.recovery.api import *
from ajenti.utils import shell


class ApacheRecovery(RecoveryProvider):
    name = 'Apache 2'
    id = 'apache'
    
    def backup(self, dir):
        shell('cp -r /etc/apache2/* %s/'%dir)
    
    def restore(self, dir):
        shell('rm /etc/apache2/* -r')
        shell('cp -r %s/* /etc/apache2/'%dir)
    
