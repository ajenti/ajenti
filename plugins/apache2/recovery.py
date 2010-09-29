from ajenti.plugins.recovery.api import SimpleDirectoryRecoveryProvider


class ApacheRecovery(SimpleDirectoryRecoveryProvider):
    name = 'Apache 2'
    id = 'apache'
    path = '/etc/apache2'
    
