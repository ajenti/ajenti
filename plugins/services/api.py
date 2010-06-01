from api import *
from ajenti.com import *

class IServiceManager(Interface):
    def list_all(self):
        pass
        
    def start(self, name):
        pass
        
    def stop(self, name):
        pass

    def restart(self, name):
        pass

        
class Service:
    name = ''
    status = ''
    
    def __cmp__(self, b):
        return 1 if self.name > b.name else -1
        
    def __str__(self):
        return self.name
